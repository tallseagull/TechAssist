const boggle = function() {
  const container = document.getElementById('js-boggle');

  let grid = [],
      isCustomGrid = false,
      customGrid;

  // Global game settings
  let settings =  {
      gridsize: 4,
      min: 3,
      max: 6,
      letters: 'AAAAAAAAABBCCDDDDDEEEEEEEEEEEEEFFGGGHHHHIIIIIIIIJKLLLLMMNNNNNOOOOOOOOPPQRRRRRRSSSSSTTTTTTTUUUUVVWWXYYZ'
  };

  /*
  * Sets up the grid size and a custom grid, if applicable
  */
  function initialiseGrid(arg) {

     let gridsize = 0,
         setLength = 0;

     if(typeof arg === 'number') {
       gridsize = arg;
     } else if(Object.prototype.toString.call(arg) === '[object Array]') {
       isCustomGrid = true;
       customGrid = arg;

       // error checking
       arg.forEach(function(set, i) {
         if(setLength === 0) {
           setLength = set.split('').length;
         }

         if(set.split('').length !== setLength) {
           throw new Error(`Custom grid sets must be of equal length. Please check customGrid at index ${i}, ${set}`);}
       });

       gridsize = arg.length;
     }

     if(gridsize < settings.min || gridsize > settings.max) {
       throw new Error(`Grid size must be between ${settings.min} and ${settings.max} inclusive`);
     }

     settings.gridsize = gridsize;

     return settings;
  }

  /*
   * Sets up the grid array
   */
  function setGrid() {

    let counter = settings.gridsize;

    if(isCustomGrid) {

      customGrid.forEach(function(set) {
        grid.push(set.toUpperCase().split(''));
      });

      return grid;
    }

    while(counter > 0) {
      grid.push(setLetters());
      counter--;
    }
    return grid;
  }

  /*
  * Sets and returns an array of random letters based on the games gridsize
  */
  function setLetters() {
    let i = 0,
        len = settings.gridsize,
        randomLetter,
        letters = [];

    for(i; i < len; i++) {
      randomLetter = settings.letters[Math.floor(Math.random() * settings.letters.length)];
      letters.push(randomLetter);
    }
    return letters;
  }

  /*
  * Renders the view of the grid
  */
  function renderGrid() {
    let render = '';

    grid.forEach(function(row) {
        render += '<div class="row">';

        row.forEach(function(letter, i) {
          render += `<span> ${letter} </span>`;
        });

        render += '</div>';
    });

    document.getElementById("js-boggle").innerHTML = render;
  }

  function init() {

      grid = [];

    if(typeof arguments[0] !== 'undefined') {
      initialiseGrid(arguments[0]);
    }

    setGrid();
    renderGrid();
  }

    // Find the button element by its id
    const shuffleButton = document.getElementById("js-shuffle");

    // Define your shuffle function
    function shuffle() {
        // Your shuffle logic here
        console.log("Shuffling...");
        document.getElementById("js-boggle").innerHTML = "";
        init();
    }

    // Add an event listener to the button
    shuffleButton.addEventListener("click", shuffle);

  return {
    init : init
  }

}();

//boggle.init(['rele', 'asin', 'spak', 'tlec']);
boggle.init(4);

