document.addEventListener("DOMContentLoaded", function () {
    const imageGrid = document.getElementById("image-grid");
    const shuffleButton = document.getElementById("js-shuffle");

    // Function to shuffle an array randomly
    function shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    }

    // Function to load and display random images
    function loadRandomImages() {
        const imageCount = 9; // Number of images to display
        const imageIndexes = Array.from({ length: 84 }, (_, i) => i + 1); // Array of image indexes (1 to 84)
        shuffleArray(imageIndexes); // Shuffle the image indexes

        // Clear the existing images
        imageGrid.innerHTML = "";

        // Load and display the random images
        for (let i = 0; i < imageCount; i++) {
            const imageIndex = imageIndexes[i];
            const img = new Image();
            img.src = `images/Picture${imageIndex}.png`;
            const imageContainer = document.createElement("div");
            imageContainer.classList.add("image-container");
            imageContainer.appendChild(img);
            imageGrid.appendChild(imageContainer);
        }
    }

    // Load and display random images when the page loads
    loadRandomImages();

    // Add a click event listener to the shuffle button
    shuffleButton.addEventListener("click", loadRandomImages);
});
