document.addEventListener("DOMContentLoaded", function () {
    const tableContainer = document.getElementById("table-container");
    const submitButton = document.getElementById("submit-button");
    const message = document.getElementById("message");
    const puzzleTable = document.getElementById("puzzle-table");

    let selectedPuzzle;
    let rowSums, colSums;

    // Load JSON data
    fetch("puzzles.json")
        .then((response) => response.json())
        .then((data) => {
            const randomIndex = Math.floor(Math.random() * data.length);
            selectedPuzzle = data[randomIndex];
            rowSums = selectedPuzzle.slice(0, 3);
            colSums = selectedPuzzle.slice(3);
            displayTable();
            displaySums();
        })
        .catch((error) => console.error(error));

    function displayTable() {
        for (let i = 0; i < 3; i++) {
            const row = document.createElement("tr");
            for (let j = 0; j < 3; j++) {
                const cell = document.createElement("td");
                const input = document.createElement("input");
                input.type = "number";
                input.min = 1;
                input.max = 9;
                cell.appendChild(input);
                row.appendChild(cell);
            }
            puzzleTable.appendChild(row);
        }
    }

    function displaySums() {
        // Add an empty cell for alignment
//        const emptyCell = document.createElement("td");
//        puzzleTable.querySelector("tr").appendChild(emptyCell);

        // Add the row sums in the last column
        const rows = puzzleTable.querySelectorAll("tr");
        for (let i = 0; i < 3; i++) {
            const sumCell = document.createElement("td");
            sumCell.classList.add("sum-label");
            sumCell.textContent = rowSums[i];
            rows[i].appendChild(sumCell);
        }

        // Add the column sums in the last row
        const newRow = document.createElement("tr");
        for (let i = 0; i < 3; i++) {
            const sumCell = document.createElement("td");
            sumCell.classList.add("sum-label");
            sumCell.textContent = colSums[i];
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

    function validateGrid(gridValues) {
        for (let i = 0; i < 3; i++) {
            let rowSum = 0;
            let colSum = 0;
            for (let j = 0; j < 3; j++) {
                rowSum += gridValues[i * 3 + j];
                colSum += gridValues[j * 3 + i];
            }

            if (rowSum !== rowSums[i] || colSum !== colSums[i]) {
                return false;
            }
        }
        return true;
    }

    // Add an event listener for the "Next puzzle" button
    const nextPuzzleButton = document.getElementById("next-puzzle-button");
    nextPuzzleButton.addEventListener("click", function () {
        location.reload(); // Reload the page to get a new puzzle
    });
});
