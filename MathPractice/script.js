let questionProbabilities = Array(11).fill().map(() => Array(11).fill(1));
let currentQuestions = [];

function generateQuestions() {
    let questions = [];
    while (questions.length < 10) {
        let row = Math.floor(Math.random() * 10) + 1;
        let col = Math.floor(Math.random() * 10) + 1;
        let probability = questionProbabilities[row][col];
        if ((Math.random() * 2) < probability) {
            questions.push({ row, col });
        }
    }
    currentQuestions = questions;
    return questions;
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
        questionElement.innerHTML = `
            <label for="q${i}">${row} x ${col} = </label>
            <input type="text" id="q${i}" name="q${i}" required>
        `;
        questionsContainer.appendChild(questionElement);
    }
}

function handleSubmit(event) {
    event.preventDefault();
    const answers = [];
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
            correctAnswerDisplay.innerHTML = ` (Correct: ${correctAnswer})`;
            input.parentNode.appendChild(correctAnswerDisplay);
        }
        answers.push({ row, col, correct });
    }
    updateProbabilities(answers);

    // Disable submit button and enable next button
    const submitButton = document.getElementById('submit-button');
    const nextButton = document.getElementById('next-button');
    submitButton.disabled = true;
    nextButton.disabled = false;
}

function handleNextClick() {
    const newQuestions = generateQuestions();
    displayQuestions(newQuestions);

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
