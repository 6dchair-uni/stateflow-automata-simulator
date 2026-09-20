import { useEffect, useState } from "react";
import "./App.css";

type State = {
  id: string;
  accepting: boolean;
};

type Transition = {
  from: string;
  symbol: string;
  to: string;
};

type Automaton = {
  type: string;
  language: string;
  states: State[];
  alphabet: string[];
  start_state: string;
  transitions: Transition[];
};

function App() {
  const [description, setDescription] = useState(
    "Binary strings ending in 01"
  );

  const [automaton, setAutomaton] = useState<Automaton | null>(null);
  const [input, setInput] = useState("");
  const [currentStates, setCurrentStates] = useState<string[]>([]);
  const [result, setResult] = useState<string | null>(null);
  const [simulating, setSimulating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [simulationSymbols, setSimulationSymbols] = useState<string[]>([]);
  const [simulationSteps, setSimulationSteps] = useState<string[][]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const SIMULATION_SPEED = 300;

  async function generate() {
    setError(null);
    setResult(null);

    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          description,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate automaton");
      }

      const data = await response.json();

      console.log("GENERATED AUTOMATON:", data);

      if (data.error) {
        setError(data.error);
        return;
      }

      setAutomaton(data);
      setCurrentStates(data.start_state);
    } catch (error) {
      console.error(error);

      setError("Could not connect to the backend.");
    }
  }

  async function simulate() {
    if (!automaton || !input.trim()) {
      return;
    }

    setResult(null);
    setError(null);
    setSimulating(true);
    setCurrentStates([]);
    setSimulationSymbols([]);
    setSimulationSteps([]);
    setCurrentStep(0);
    setIsPlaying(false);

    try {
      const response = await fetch("/api/simulate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          input,
          automaton,
        }),
      });

      if (!response.ok) {
        throw new Error("Simulation failed");
      }

      const data = await response.json();

      if (data.error) {
        setError(data.error);
        return;
      }

      setSimulationSymbols(data.symbols ?? []);
      setSimulationSteps(data.steps ?? []);

      if (data.steps?.length) {
        const initialStates = data.steps[0];

        setCurrentStep(0);
        setCurrentStates(initialStates);
        setResult(null);
        setIsPlaying(true);
      }
    } catch (error) {
      console.error(error);

      setError("Could not connect to the backend.");
    } finally {
      setSimulating(false);
    }
  }

  /*
   * Animate the simulation one state at a time.
   * The speed is controlled by SIMULATION_SPEED.
   */

  useEffect(() => {
    if (!isPlaying || simulationSteps.length === 0) {
      return;
    }

    const timer = setTimeout(() => {
      const nextStep = currentStep + 1;

      if (nextStep >= simulationSteps.length) {
        const finalStep = simulationSteps[simulationSteps.length - 1];

        setCurrentStep(simulationSteps.length - 1);
        setCurrentStates(finalStep);
        setIsPlaying(false);

        // Determine final result
        const finalAutomatonStates = automaton?.states.filter((state) =>
          finalStep.includes(state.id)
        );

        const accepted =
          finalAutomatonStates?.some((state) => state.accepting) ?? false;

        setResult(accepted ? "ACCEPTED" : "REJECTED");

        return;
      }

      const nextStates = simulationSteps[nextStep];

      setCurrentStep(nextStep);
      setCurrentStates(nextStates);
    }, SIMULATION_SPEED);

    return () => clearTimeout(timer);
  }, [isPlaying, currentStep, simulationSteps, automaton]);

  function playSimulation() {
    if (!simulationSteps.length) {
      return;
    }

    if (currentStep >= simulationSteps.length - 1) {
      return;
    }

    setIsPlaying(true);
    setResult(null);
  }

  function pauseSimulation() {
    setIsPlaying(false);
  }

  function resetSimulation() {
    if (!automaton) {
      return;
    }

    setIsPlaying(false);
    setCurrentStep(0);
    setCurrentStates([automaton.start_state]);
    setResult(null);
  }

  /*
   * Arrange states around a circle.
   * This gives the automaton a graph-like layout
   * instead of a purely horizontal arrangement.
   */

  function getStatePosition(index: number, total: number) {
    const centerX = 500;
    const centerY = 350;

    if (total === 1) {
      return {
        x: centerX,
        y: centerY,
      };
    }

    const radius = total <= 4 ? 150 : total <= 8 ? 220 : 270;

    const angle = (2 * Math.PI * index) / total - Math.PI / 2;

    return {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle),
    };
  }

  function getStatePositionById(id: string) {
    if (!automaton) {
      return {
        x: 0,
        y: 0,
      };
    }

    const index = automaton.states.findIndex((state) => state.id === id);

    return getStatePosition(index, automaton.states.length);
  }

  return (
    <main className="app">
      <header className="app-header">
        <h1>StateFlow: Automata Simulator</h1>

        <p>Interactive formal language and automata simulator</p>
      </header>

      <div className="workspace">
        <aside className="sidebar">
          <section>
            <h2>Language Description</h2>

            <textarea
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Describe the language..."
              rows={4}
            />

            <button
              onClick={generate}
              disabled={!description.trim() || simulating}
            >
              Generate Automaton
            </button>
          </section>

          {automaton && (
            <section>
              <h2>Automaton</h2>

              <div className="type-badge">{automaton.type}</div>

              <div className="language-box">{automaton.language}</div>
            </section>
          )}

          {automaton && (
            <section>
              <h2>Sample Input</h2>

              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="e.g. 1101"
              />

              <button onClick={simulate} disabled={simulating || !input.trim()}>
                {simulating ? "Simulating..." : "Simulate"}
              </button>
            </section>
          )}

          <div className="simulation-controls">
            <button
              onClick={playSimulation}
              disabled={
                !simulationSteps.length ||
                isPlaying ||
                currentStep >= simulationSteps.length - 1
              }
            >
              ▶ Play
            </button>

            <button onClick={pauseSimulation} disabled={!isPlaying}>
              ⏸ Pause
            </button>

            <button
              onClick={resetSimulation}
              disabled={!simulationSteps.length}
            >
              ↻ Reset
            </button>
          </div>

          {simulationSymbols.length > 0 && (
            <section className="simulation-info">
              <h2>Simulation</h2>

              <div className="input-display">
                {simulationSymbols.map((symbol, index) => (
                  <span
                    key={index}
                    className={
                      index === currentStep - 1
                        ? "input-symbol active"
                        : "input-symbol"
                    }
                  >
                    {symbol}
                  </span>
                ))}
              </div>

              {currentStep > 0 && currentStep <= simulationSymbols.length && (
                <div className="step-info">
                  <div>
                    Reading symbol:{" "}
                    <strong>{simulationSymbols[currentStep - 1]}</strong>
                  </div>

                  <div>
                    Transition:{" "}
                    <strong>{simulationSteps[currentStep - 1]}</strong>
                    {" → "}
                    <strong>{simulationSteps[currentStep]}</strong>
                  </div>
                </div>
              )}
            </section>
          )}

          {error && (
            <section className="result">
              <h2>Error</h2>

              <div className="rejected">{error}</div>
            </section>
          )}

          {result && (
            <section className="result">
              <h2>Result</h2>

              <div className={result === "ACCEPTED" ? "accepted" : "rejected"}>
                {result}
              </div>
            </section>
          )}
        </aside>

        <section className="canvas-panel">
          <div className="canvas-header">
            <h2>Automaton</h2>

            {automaton && (
              <span>
                {automaton.states.length} states · Alphabet:{" "}
                {"{"}
                {automaton.alphabet.join(", ")}
                {"}"}
              </span>
            )}
          </div>

          {!automaton && (
            <div className="empty-state">
              <p>Describe a language and generate an automaton.</p>
            </div>
          )}

          {automaton && (
            <svg className="automaton" viewBox="0 0 1000 700">
              <defs>
                <marker
                  id="arrow"
                  viewBox="0 0 10 10"
                  refX="9"
                  refY="5"
                  markerWidth="7"
                  markerHeight="7"
                  orient="auto"
                >
                  <path d="M 0 0 L 10 5 L 0 10 z" />
                </marker>
              </defs>

              {/* -------------------------------- */}
              {/* Transitions                      */}
              {/* -------------------------------- */}

              {automaton.transitions.map((transition, index) => {
                const from = getStatePositionById(transition.from);
                const to = getStatePositionById(transition.to);

                const sameState = transition.from === transition.to;

                /*
                 * Self-loop
                 */
                if (sameState) {
                  return (
                    <g key={index}>
                      <path
                        d={`
                          M ${from.x - 20} ${from.y - 35}
                          C
                          ${from.x - 80} ${from.y - 130},
                          ${from.x + 80} ${from.y - 130},
                          ${from.x + 20} ${from.y - 35}
                        `}
                        fill="none"
                        markerEnd="url(#arrow)"
                      />

                      <text
                        x={from.x}
                        y={from.y - 105}
                        textAnchor="middle"
                        className="transition-label"
                      >
                        {transition.symbol}
                      </text>
                    </g>
                  );
                }

                /*
                 * Normal transition
                 *
                 * Offset the line perpendicular to the
                 * from→to direction so that transitions
                 * going opposite ways between the same
                 * two states don't overlap.
                 */

                const dx = to.x - from.x;
                const dy = to.y - from.y;

                const distance = Math.sqrt(dx * dx + dy * dy) || 1;

                const offsetX = (-dy / distance) * 12;
                const offsetY = (dx / distance) * 12;

                const startX = from.x + (dx / distance) * 40 + offsetX;
                const startY = from.y + (dy / distance) * 40 + offsetY;

                const endX = to.x - (dx / distance) * 40 + offsetX;
                const endY = to.y - (dy / distance) * 40 + offsetY;

                const midX = (startX + endX) / 2;
                const midY = (startY + endY) / 2;

                return (
                  <g key={index}>
                    <line
                      x1={startX}
                      y1={startY}
                      x2={endX}
                      y2={endY}
                      markerEnd="url(#arrow)"
                    />

                    <text
                      x={midX}
                      y={midY - 12}
                      textAnchor="middle"
                      className="transition-label"
                    >
                      {transition.symbol}
                    </text>
                  </g>
                );
              })}

              {/* -------------------------------- */}
              {/* Start arrow                      */}
              {/* -------------------------------- */}

              {(() => {
                const start = getStatePositionById(automaton.start_state);

                return (
                  <g>
                    <line
                      x1={start.x - 100}
                      y1={start.y}
                      x2={start.x - 42}
                      y2={start.y}
                      markerEnd="url(#arrow)"
                    />

                    <text
                      x={start.x - 85}
                      y={start.y - 20}
                      textAnchor="middle"
                      className="transition-label"
                    >
                      start
                    </text>
                  </g>
                );
              })()}

              {/* -------------------------------- */}
              {/* States                           */}
              {/* -------------------------------- */}

              {automaton.states.map((state, index) => {
                const position = getStatePosition(
                  index,
                  automaton.states.length
                );

                const active = currentStates.includes(state.id);

                return (
                  <g key={state.id}>
                    <circle
                      cx={position.x}
                      cy={position.y}
                      r="40"
                      className={active ? "state active" : "state"}
                    />

                    {state.accepting && (
                      <circle
                        cx={position.x}
                        cy={position.y}
                        r="32"
                        className="accepting-ring"
                      />
                    )}

                    <text
                      x={position.x}
                      y={position.y + 6}
                      textAnchor="middle"
                      className="state-label"
                    >
                      {state.id}
                    </text>
                  </g>
                );
              })}
            </svg>
          )}
        </section>
      </div>
    <footer className="app-footer">
    © 2024–2026 6dchair
        <div className="footer-links">
            <a href="mailto:gracedave.work@gmail.com">
            Email_me
            </a>

            <a
            href="https://6dworkportfolio.vercel.app/"
            target="_blank"
            rel="noopener noreferrer"
            >
            Portfolio ↗
            </a>
      </div>
    </footer>

    </main>
  );
}

export default App;