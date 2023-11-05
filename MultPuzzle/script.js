document.addEventListener("DOMContentLoaded", function () {
    const tableContainer = document.getElementById("table-container");
    const submitButton = document.getElementById("submit-button");
    const message = document.getElementById("message");
    const puzzleTable = document.getElementById("puzzle-table");

    let selectedPuzzle;
    const gridSize = 2;

    // Generate a puzzle - pick 4 random numbers in a 2x2 grid. Numbers are between 1-10. For each row and column calculate the product of the numbers:
    function generatePuzzle(gridSize) {
      // Generate random numbers between 1 and 10
      const numbers = [];
      for (let i = 0; i < gridSize * gridSize; i++) {
        numbers.push(Math.floor(Math.random() * 10) + 1);
      }

      // Calculate row and column Prods
      const rowProds = [];
      const colProds = [];
      for (let i = 0; i < gridSize; i++) {
        let rowSum = 1;
        let colSum = 1;
        for (let j = 0; j < gridSize; j++) {
          rowSum *= numbers[i * gridSize + j];
          colSum *= numbers[i + j * gridSize];
        }
        rowProds.push(rowSum);
        colProds.push(colSum);
      }

      // Return the row and column Prods
      return {
        rowProds,
        colProds
      };
    }

    function displayTable(gridSize) {
        for (let i = 0; i < gridSize; i++) {
            const row = document.createElement("tr");
            for (let j = 0; j < gridSize; j++) {
                const cell = document.createElement("td");
                const input = document.createElement("input");
                input.type = "number";
                input.min = 1;
                input.max = 10;
                cell.appendChild(input);
                row.appendChild(cell);
            }
            puzzleTable.appendChild(row);
        }
    }

    function displayProds(gridSize, colProds, rowProds) {
        // Add the row Prods in the last column
        const rows = puzzleTable.querySelectorAll("tr");
        for (let i = 0; i < gridSize; i++) {
            const sumCell = document.createElement("td");
            sumCell.classList.add("sum-label");
            sumCell.textContent = rowProds[i];
            rows[i].appendChild(sumCell);
        }

        // Add the column Prods in the last row
        const newRow = document.createElement("tr");
        for (let i = 0; i < gridSize; i++) {
            const sumCell = document.createElement("td");
            sumCell.classList.add("sum-label");
            sumCell.textContent = colProds[i];
            newRow.appendChild(sumCell);
        }
        puzzleTable.appendChild(newRow);
    }

    function showFireworks() {
        const fireworksContainer = document.getElementById('fireworks');
        fireworksContainer.style.display = 'block';

        setTimeout(() => {
            fireworksContainer.style.display = 'none';
        }, 30000);
    }

    submitButton.addEventListener("click", function () {
        const inputs = document.querySelectorAll("#puzzle-table input");
        const gridValues = Array.from(inputs).map((input) => parseInt(input.value, 10));

        if (validateGrid(gridValues)) {
            message.textContent = "Congratulations! You solved the puzzle.";
            message.style.color = "green";
            showFireworks();
        } else {
            message.textContent = "Try again. Your solution is incorrect.";
            message.style.color = "red";
        }
    });

    function validateGrid(gridValues, gridSize) {
        for (let i = 0; i < gridSize; i++) {
            let rowProd = 1;
            let colProd = 1;
            for (let j = 0; j < gridSize; j++) {
                rowSum *= gridValues[i * gridSize + j];
                colSum *= gridValues[j * gridSize + i];
            }

            if (rowProd !== rowProds[i] || colProd !== colProds[i]) {
                return false;
            }
        }
        return true;
    }

    // Generate a puzzle
    const puzzle = generatePuzzle(gridSize);
    displayTable(gridSize);
    displayProds(gridSize, puzzle.colProds, puzzle.rowProds);

    // Add an event listener for the "Next puzzle" button
    const nextPuzzleButton = document.getElementById("next-puzzle-button");
    nextPuzzleButton.addEventListener("click", function () {
        // Remove the existing puzzle table
        puzzleTable.innerHTML = "";

        // Stop the fireworks
        const fireworksContainer = document.getElementById('fireworks');
        fireworksContainer.style.display = 'none';

        // Generate a new puzzle
        const puzzle = generatePuzzle(gridSize);
        displayTable(gridSize);
        displayProds(gridSize, puzzle.colProds, puzzle.rowProds);
    });
});
