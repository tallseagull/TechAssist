let questionProbabilities = Array(11).fill().map(() => Array(11).fill(1));
let currentQuestions = [];
let level = 5; // Initialize the level

function generateQuestions() {
    let questions = [];
    while (questions.length < 10) {
        let row = Math.floor(Math.random() * level) + 1;
        let col = Math.floor(Math.random() * level) + 1;
        let probability = questionProbabilities[row][col];
        // Reduce probability if row=1 or col=1:
        if ((row==1) || (col==1)) {
            probability = probability / 3.0;
        }
        if ((Math.random() * 2) < probability) {
            if (isNewQuestion(row, col, questions)) {
                questions.push({ row, col });
            }
        }
    }
    currentQuestions = questions;
    return questions;
}

function isNewQuestion(row, col, questions) {
    // Check if the question is already in our list:
    for (let i=0; i < questions.length; i++) {
        if ((row===questions[i].row) && (col===questions[i].col)) {
            return false;
        }
    }
    return true;
}

function updateLevelDisplay() {
    const levelDisplay = document.getElementById('level-display');
    levelDisplay.textContent = `רמה: ${level}`;
}


function updateProbabilities(answers) {
    for (let i = 0; i < answers.length; i++) {
        let { row, col, correct } = answers[i];
        if (correct) {
            questionProbabilities[row][col] = Math.max(questionProbabilities[row][col] - 0.2, 0.0);
        } else {
            questionProbabilities[row][col] += 0.2;
        }
    }
}

function displayQuestions(questions) {
    const questionsContainer = document.getElementById('questions');
    questionsContainer.innerHTML = '';
    for (let i = 0; i < questions.length; i++) {
        const { row, col } = questions[i];
        const questionElement = document.createElement('div');
        questionElement.classList.add("qfield");
        questionElement.innerHTML = `
            <label for="q${i}">${row} x ${col} = </label>
            <input type="text" id="q${i}" name="q${i}" required>
        `;
        questionsContainer.appendChild(questionElement);
    }
}

function showFireworks() {
    const fireworksContainer = document.getElementById('fireworks');
    fireworksContainer.style.display = 'block';

    setTimeout(() => {
        fireworksContainer.style.display = 'none';
    }, 30000);
}

function handleSubmit(event) {
    event.preventDefault();
    const answers = [];
    let allCorrect = true; // Flag to check if all answers are correct
    for (let i = 0; i < 10; i++) {
        const input = document.getElementById(`q${i}`);
//        const userAnswer = parseInt(input.value, 10);
        let userAnswer = -1; // Default value in case of an exception
        try {
            userAnswer = parseInt(input.value, 10);
            if (isNaN(userAnswer)) {
                userAnswer = -1;
            }
        } catch (error) {
            console.error('Error parsing user answer:', error);
        }

        const { row, col } = currentQuestions[i];
        const correctAnswer = row * col;
        const correct = userAnswer === correctAnswer;
        if (!correct) {
            input.classList.add('wrong-answer');
            const correctAnswerDisplay = document.createElement('span');
            correctAnswerDisplay.innerHTML = `( ${correctAnswer} )`;
            input.parentNode.appendChild(correctAnswerDisplay);
            allCorrect = false;
        } else {
            input.classList.add('correct-answer'); // Apply correct-answer class
        }
        answers.push({ row, col, correct });
    }
    updateProbabilities(answers);

    // Disable submit button and enable next button
    const submitButton = document.getElementById('submit-button');
    const nextButton = document.getElementById('next-button');
    submitButton.disabled = true;
    nextButton.disabled = false;

    // Show fireworks if all answers are correct
    if (allCorrect) {
        if (level < 10) {
            level++;
            updateLevelDisplay();
        }
        showFireworks();
    }
}

function handleNextClick() {
    const newQuestions = generateQuestions();
    displayQuestions(newQuestions);

    // Disable the fireworks:
    const fireworksContainer = document.getElementById('fireworks');
    fireworksContainer.style.display = 'none';

    // Enable submit button and disable next button
    const submitButton = document.getElementById('submit-button');
    const nextButton = document.getElementById('next-button');
    submitButton.disabled = false;
    nextButton.disabled = true;
}

const questions = generateQuestions();
displayQuestions(questions);

const submitButton = document.getElementById('submit-button');
const nextButton = document.getElementById('next-button');
submitButton.addEventListener('click', handleSubmit);
nextButton.addEventListener('click', handleNextClick);
