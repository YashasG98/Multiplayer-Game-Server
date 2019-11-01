class Connect4 {
    constructor(selector) {
        this.ROWS = 6;
        this.COLS = 7;
        this.player = '';
        this.turn = 'red';
        this.selector = selector;
        this.isGameOver = false;
        this.rowOfCellClicked = null;
        this.colOfCellClicked = null;
        this.onPlayerMove = function () { };
        this.createGrid();
        this.setupEventListeners();
        this.fillCell = function (r, c, p) {
            var $cell;
            $cell = $(`.col[data-row='${r}'][data-col='${c}']`);
            $cell.removeClass(`empty next-${p}`);
            $cell.addClass(`${p}`);
            $cell.data('player', `${p}`);
        };
    }

    createGrid() {
        const $board = $(this.selector);
        $board.empty();
        this.isGameOver = false;
        this.player = 'red';
        for (let row = 0; row < this.ROWS; row++) {
            const $row = $('<div>')
                .addClass('row');
            for (let col = 0; col < this.COLS; col++) {
                const $col = $('<div>')
                    .addClass('col empty')
                    .attr('data-col', col)
                    .attr('data-row', row);
                $row.append($col);
            }
            $board.append($row);
        }
    }

    setupEventListeners() {
        const $board = $(this.selector);
        const that = this;

        function findLastEmptyCell(col) {
            const cells = $(`.col[data-col='${col}']`);
            for (let i = cells.length - 1; i >= 0; i--) {
                const $cell = $(cells[i]);
                if ($cell.hasClass('empty')) {
                    return $cell;
                }
            }
            return null;
        }

        $board.on('mouseenter', '.col.empty', function () {
            if (that.isGameOver) return;
            const col = $(this).data('col');
            const $lastEmptyCell = findLastEmptyCell(col);
            $lastEmptyCell.addClass(`next-${that.player}`);
        });

        $board.on('mouseleave', '.col', function () {
            $('.col').removeClass(`next-${that.player}`);
        });

        $board.on('click', '.col.empty', function () {
            if (that.isGameOver) return;

            if (that.player === that.turn) {
                const col = $(this).data('col');
                const $lastEmptyCell = findLastEmptyCell(col);
                $lastEmptyCell.removeClass(`empty next-${that.player}`);
                $lastEmptyCell.addClass(that.player);
                $lastEmptyCell.data('player', that.player);

                that.rowOfCellClicked = $lastEmptyCell.data('row');
                that.colOfCellClicked = $lastEmptyCell.data('col');

                const winner = that.checkForWinner($lastEmptyCell.data('row'),
                    $lastEmptyCell.data('col'));

                if (winner) {
                    that.isGameOver = true;
                    alert(`Game Over! You have won!`);
                    $('.col.empty').removeClass('empty');
                    that.onPlayerMove();
                    return;
                }

                that.turn = (that.turn === 'red') ? 'black' : 'red';
                that.onPlayerMove();
                $(this).trigger('mouseenter');
            }
        });
    }

    checkForWinner(row, col) {
        const that = this;

        function $getCell(i, j) {
            return $(`.col[data-row='${i}'][data-col='${j}']`);
        }

        function checkDirection(direction) {
            let total = 0;
            let i = row + direction.i;
            let j = col + direction.j;
            let $next = $getCell(i, j);
            while (i >= 0 && i < that.ROWS && j >= 0 && j < that.COLS &&
                $next.data('player') === that.player) {
                total++;
                i += direction.i;
                j += direction.j;
                $next = $getCell(i, j);
            }
            return total;
        }

        function checkWin(directionA, directionB) {
            const total = 1 +
                checkDirection(directionA) +
                checkDirection(directionB);
            if (total >= 4) {
                return that.player;
            } else {
                return null;
            }
        }

        function checkDiagonalBLtoTR() {
            return checkWin({ i: -1, j: 1 }, { i: 1, j: -1 });
        }

        function checkDiagonalTLtoBR() {
            return checkWin({ i: 1, j: 1 }, { i: -1, j: -1 });
        }

        function checkVerticals() {
            return checkWin({ i: -1, j: 0 }, { i: 1, j: 0 });
        }

        function checkHorizontals() {
            return checkWin({ i: 0, j: -1 }, { i: 0, j: 1 });
        }

        return checkVerticals() ||
            checkHorizontals() ||
            checkDiagonalBLtoTR() ||
            checkDiagonalTLtoBR();

    }

    restart() {
        this.createGrid();
        this.onPlayerMove();
    }
}

$(document).ready(function () {
    const connect4 = new Connect4('#connect4')
    var socket = io('http://127.0.0.1:5000/private');
    connect4.player = playerColor;

    socket.emit('user_email', {'player': user, 'game_id': 2});
    socket.emit('redirectionSocket', {'player': user, 'game_id': 2});

    connect4.onPlayerMove = function () {
        socket.emit('board', {
            'row': connect4.rowOfCellClicked,
            'col': connect4.colOfCellClicked,
            'player': connect4.player,
            'turn': connect4.turn,
            'game_over': connect4.isGameOver,
            'user': user
        });
    }
    
    socket.on('game_state', data => {
        if (data['game_over']){
            alert(`Game Over! ${data['user']} wins the game`);
        } else {
            connect4.turn = data['turn'];
        }
        connect4.fillCell(data['row'], data['col'], data['player']);
    });
});