class Player {

    constructor() {
        this.spot = -1;
        this.roll = -1;
        this.next = -1;
        this.state = 1;
    }

    rollDie() {
        this.roll = floor(random(1, 7));
        // this.roll = 20;
        this.next = this.spot + this.roll;
        return this.roll;
    }

    move() {
        this.spot = this.next;
    }

    showPreview(color) {
        let start = max(0, this.spot);
        let end = min(this.next, tiles.length - 1);
        for (let i = start; i <= end; i++) {
            tiles[i].highlight(color);
        }
    }

    isSnadder() {
        let tile = tiles[this.spot];
        if (tile && tile.snadder !== 0)
            return true;
        else
            return false;
    }

    moveSnadder(){
        let tile = tiles[this.spot];
        this.spot += tile.snadder;
    }

    show(color) {
        let current = tiles[this.spot];
        if (!current) return;
        fill(color);
        let center = current.getCenter();
        ellipse(center[0], center[1], 32, 32);
    }
}