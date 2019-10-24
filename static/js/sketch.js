const ROLL_STATE = 0;
const MOVE_STATE = 1;
const SNADDER_STATE = 2;
let state = ROLL_STATE;


let tiles = [];
let player;

function setup() {
    var myCanvas = createCanvas(600, 600);
    myCanvas.parent("board");
    
    let resolution = 60;
    let cols = width / resolution;
    let rows = height / resolution;

    let x = 0;
    let y = (rows - 1) * resolution;
    let dir = 1;
    for (let i = 0; i < cols * rows; i++) {
        let tile = new Tile(x, y, resolution, i, i + 1);
        tiles.push(tile);
        x = x + (resolution * dir);
        if (x >= width || x <= -resolution) {
            dir *= -1;
            x += resolution * dir;
            y -= resolution;
        }
    }

    // for (let i = 0; i < 3; i++) {
    //     let index = floor(random(cols, tiles.length));
    //     tiles[index].snadder = -1 * floor(random(index % cols, index - 1));
    // }

    // for (let i = 0; i < 3; i++) {
    //     let index = floor(random(0, tiles.length - cols));
    //     tiles[index].snadder = floor(random(cols - (index % cols), tiles.length - index - 1));
    // }

    player = new Player();
}

function draw() {

    background(51);

    for (let tile of tiles) {
        tile.show();
    }

    for (let tile of tiles) {
        tile.showSnadders(tiles);
    }

    if (state == ROLL_STATE) {
        var x = player.rollDie();
        if(x==1){
            document.getElementById("diceImg").src = '../static/images/dice1.png';
        }else if(x==2){
            document.getElementById("diceImg").src = '../static/images/dice2.png';
        }else if(x==3){
            document.getElementById("diceImg").src = '../static/images/dice3.png';
        }else if(x==4){
            document.getElementById("diceImg").src = '../static/images/dice4.png';
        }else if(x==5){
            document.getElementById("diceImg").src = '../static/images/dice5.png';
        }else if(x==6){
            document.getElementById("diceImg").src = '../static/images/dice6.png';
        }
        player.showPreview();
        state = MOVE_STATE;
    }
    else if (state == MOVE_STATE) {
        player.move();
        if (player.isSnadder()) {
            state = SNADDER_STATE;
        }
        else {
            state = ROLL_STATE;
        }
    } 
    else if (state == SNADDER_STATE){
        player.moveSnadder();
        state = ROLL_STATE;
    }

    if (player.spot >= tiles.length - 1) {
        player.spot = tiles.length - 1;
        console.log("game over");
        noLoop();
    }

    player.show();
    noLoop();
}

function rollOnce() {
    if (player.spot >= tiles.length - 1) {
        player.spot = tiles.length - 1;
        alert("Game over!");
        noLoop();
    }
    else 
        redraw();
}