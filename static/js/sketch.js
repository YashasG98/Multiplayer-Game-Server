const ROLL_STATE = 0;
const MOVE_STATE = 1;
const SNADDER_STATE = 2;

let active_player = 1;

let tiles = [];
let player1;
let player2;

let lastMoveValue;

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

    tiles[39].snadder = -37;
    tiles[26].snadder = -22;
    tiles[42].snadder = -25;
    tiles[53].snadder = -23;
    tiles[65].snadder = -21;
    tiles[75].snadder = -18;
    tiles[88].snadder = -36;
    tiles[98].snadder = -58;
    tiles[3].snadder = 21;
    tiles[12].snadder = 33;
    tiles[41].snadder = 21;
    tiles[49].snadder = 19;
    tiles[32].snadder = 16;
    tiles[61].snadder = 19;
    tiles[73].snadder = 18;

    player1 = new Player();
    player2 = new Player();
    player2.state = ROLL_STATE;
}

function draw() {

    background(51);

    for (let tile of tiles) {
        tile.show();
    }

    for (let tile of tiles) {
        tile.showSnadders(tiles);
    }

    if (active_player == 1) {
        if (player1.state == ROLL_STATE) {
            if(!isPlayer2)
                lastMoveValue = player1.rollDie();
            if (!isPlayer2) {
                if (lastMoveValue == 1) {
                    document.getElementById("diceImg").src = '../static/images/dice1.png';
                } else if (lastMoveValue == 2) {
                    document.getElementById("diceImg").src = '../static/images/dice2.png';
                } else if (lastMoveValue == 3) {
                    document.getElementById("diceImg").src = '../static/images/dice3.png';
                } else if (lastMoveValue == 4) {
                    document.getElementById("diceImg").src = '../static/images/dice4.png';
                } else if (lastMoveValue == 5) {
                    document.getElementById("diceImg").src = '../static/images/dice5.png';
                } else if (lastMoveValue == 6) {
                    document.getElementById("diceImg").src = '../static/images/dice6.png';
                }
            }
            player1.showPreview([0, 255, 0, 100]);
            player1.state = MOVE_STATE;
        }
        else if (player1.state == MOVE_STATE) {
            player1.move();
            if (player1.isSnadder()) {
                player1.state = SNADDER_STATE;
            }
            else {
                player1.state = ROLL_STATE;
            }
        }
        else if (player1.state == SNADDER_STATE) {
            player1.moveSnadder();
            player1.state = ROLL_STATE;
        }

        if (player1.spot >= tiles.length - 1) {
            player1.spot = tiles.length - 1;
            console.log("game over");
            noLoop();
        }
    } else {
        if (player2.state == ROLL_STATE) {
            if (isPlayer2)
                lastMoveValue = player2.rollDie();
            if (isPlayer2) {
                if (lastMoveValue == 1) {
                    document.getElementById("diceImg").src = '../static/images/dice1.png';
                } else if (lastMoveValue == 2) {
                    document.getElementById("diceImg").src = '../static/images/dice2.png';
                } else if (lastMoveValue == 3) {
                    document.getElementById("diceImg").src = '../static/images/dice3.png';
                } else if (lastMoveValue == 4) {
                    document.getElementById("diceImg").src = '../static/images/dice4.png';
                } else if (lastMoveValue == 5) {
                    document.getElementById("diceImg").src = '../static/images/dice5.png';
                } else if (lastMoveValue == 6) {
                    document.getElementById("diceImg").src = '../static/images/dice6.png';
                }
            }
            player2.showPreview([0, 0, 255, 100]);
            player2.state = MOVE_STATE;
        }
        else if (player2.state == MOVE_STATE) {
            player2.move();
            if (player2.isSnadder()) {
                player2.state = SNADDER_STATE;
            }
            else {
                player2.state = ROLL_STATE;
            }
        }
        else if (player2.state == SNADDER_STATE) {
            player2.moveSnadder();
            player2.state = ROLL_STATE;
        }

        if (player2.spot >= tiles.length - 1) {
            player2.spot = tiles.length - 1;
            console.log("game over");
            noLoop();
        }
    }

    player1.show([0, 255, 0]);
    player2.show([0, 0, 255]);

    noLoop();
}

function rollOnce() {

    if (player1.spot >= tiles.length - 1) {
        player1.spot = tiles.length - 1;
        alert("Game over!");
        noLoop();
    }
    else if (player2.spot >= tiles.length - 1) {
        player2.spot = tiles.length - 1;
        alert("Game over!");
        noLoop();
    }
    else {
        if (active_player == 1) {
            if (player1.state == ROLL_STATE) {
                redraw();
                setTimeout(function () {
                    redraw();
                    if (player1.state == SNADDER_STATE)
                        redraw();
                    if (isPlayer2)
                        $('#rollButton').removeAttr('disabled');
                    else{
                        arr= [lastMoveValue,user_email]
                        socket_private.emit('moveSender', arr);
                        // console.log('HERE1');
                        $('#rollButton').attr('disabled', 'disabled');
                    }
                    active_player = 2;
                }, 750);
            }
            else if (player1.state == MOVE_STATE) {
                redraw();
                active_player = 2;
            }

        } else {
            if (player2.state == ROLL_STATE) {
                redraw();
                setTimeout(function () {
                    redraw();
                    if (player2.state == SNADDER_STATE)
                        redraw();
                    if (isPlayer2){
                        $('#rollButton').attr('disabled', 'disabled');
                        arr= [lastMoveValue,user_email]
                        socket_private.emit('moveSender', arr);
                        // console.log('HERE2');
                    }
                    else
                        $('#rollButton').removeAttr('disabled');
                    active_player = 1;
                }, 750);
            }
            else if (player2.state == MOVE_STATE) {
                redraw();
                active_player = 1;
            }

        }
    }
}