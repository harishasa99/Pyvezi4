document.addEventListener("DOMContentLoaded", () => {
  const gameSetupForm = document.getElementById("game-setup");
  const startGameBtn = document.getElementById("start-game-btn");
  const gameBoardContainer = document.getElementById("game-board-container");
  const gameBoard = document.getElementById("game-board");
  const turnInfo = document.getElementById("turn-info");
  const restartBtn = document.getElementById("restart-btn");

  let currentPlayer = "Crveni";
  let gameState = null;
  let isComputerYellow = false;
  let isComputerRed = false;

  const renderGameBoard = (state) => {
    gameBoard.innerHTML = "";
    state.board.forEach((row, rowIndex) => {
      row.forEach((cell, colIndex) => {
        const cellDiv = document.createElement("div");
        cellDiv.classList.add("tile");
        cellDiv.dataset.column = colIndex;

        if (cell === 1) {
          const redChecker = document.createElement("img");
          redChecker.src = "/static/images/red.png";
          redChecker.alt = "Crveni";
          cellDiv.appendChild(redChecker);
        } else if (cell === 2) {
          const yellowChecker = document.createElement("img");
          yellowChecker.src = "/static/images/yellow.png";
          yellowChecker.alt = "Žuti";
          cellDiv.appendChild(yellowChecker);
        }

        gameBoard.appendChild(cellDiv);
      });
    });
  };

  const updateTurnInfo = (message) => {
    turnInfo.textContent = message;
  };

  const startGame = () => {
    const gameMode = document.getElementById("game-mode").value;
    const difficulty = document.getElementById("difficulty").value;

    isComputerRed =
      gameMode === "human-vs-computer" || gameMode === "computer-vs-computer";
    isComputerYellow = gameMode === "computer-vs-computer";

    const playerRed = isComputerRed ? "competitive" : "human";
    const playerYellow = isComputerYellow ? "competitive" : "human";
    const maxDepth =
      difficulty === "easy" ? 3 : difficulty === "medium" ? 5 : 7;

    fetch("/start_game/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        player_red: playerRed,
        player_yellow: playerYellow,
        max_depth: maxDepth,
        moves: [],
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log("Game started:", data);
        gameState = data.state;

        // Sakrij konfiguraciju i prikaži tablu za igru
        gameSetupForm.style.display = "none";
        gameBoardContainer.style.display = "block";

        renderGameBoard(gameState);
        updateTurnInfo(`Na potezu: ${currentPlayer}`);

        if (isComputerRed) {
          playComputerTurn();
        }
      })
      .catch((error) => {
        console.error("Error starting the game:", error);
      });
  };

  const playComputerTurn = () => {
    fetch("/play_turn/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ column: null }), // Računar bira potez
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          console.error(data.error);
          return;
        }

        gameState = data.state;
        renderGameBoard(gameState);

        if (data.message.includes("wins") || data.message.includes("Draw")) {
          updateTurnInfo(data.message);
        } else {
          currentPlayer = currentPlayer === "Crveni" ? "Žuti" : "Crveni";
          updateTurnInfo(`Na potezu: ${currentPlayer}`);

          if (
            (currentPlayer === "Crveni" && isComputerRed) ||
            (currentPlayer === "Žuti" && isComputerYellow)
          ) {
            setTimeout(playComputerTurn, 1000); // Pauza pre sledećeg poteza
          }
        }
      })
      .catch((error) => {
        console.error("Error playing turn:", error);
      });
  };

  const playHumanTurn = (column) => {
    fetch("/play_turn/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ column }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          alert(data.error);
          return;
        }

        gameState = data.state;
        renderGameBoard(gameState);

        if (data.message.includes("wins") || data.message.includes("Draw")) {
          updateTurnInfo(data.message);
        } else {
          currentPlayer = currentPlayer === "Crveni" ? "Žuti" : "Crveni";
          updateTurnInfo(`Na potezu: ${currentPlayer}`);

          if (
            (currentPlayer === "Crveni" && isComputerRed) ||
            (currentPlayer === "Žuti" && isComputerYellow)
          ) {
            playComputerTurn();
          }
        }
      })
      .catch((error) => {
        console.error("Error playing turn:", error);
      });
  };

  startGameBtn.addEventListener("click", startGame);

  gameBoard.addEventListener("click", (event) => {
    if (
      (currentPlayer === "Crveni" && !isComputerRed) ||
      (currentPlayer === "Žuti" && !isComputerYellow)
    ) {
      const column = event.target.dataset.column;
      if (column !== undefined) {
        playHumanTurn(parseInt(column, 10));
      }
    }
  });

  restartBtn.addEventListener("click", () => {
    location.reload();
  });
});
