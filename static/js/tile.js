class Tile{
    constructor(x,y,wh,index, next){
        this.x = x;
        this.y = y;
        this.wh = wh;
        this.index = index;
        this.next = next;
        this.snadder = 0;
        if (this.index % 2 ==0)
        this.color = 200;
        else
        this.color = 100;
    }

    getCenter(){
        let cx = this.x + this.wh /2;
        let cy = this.y + this.wh /2;
        return [cx,cy];
     }

    show() {
        fill(this.color);
        noStroke();
        rect(this.x, this.y, this.wh, this.wh);
    }

    highlight(color) {
        fill(color);
        noStroke();
        rect(this.x, this.y, this.wh, this.wh);
    }

    showSnadders(){
        if(this.snadder !=0 ){
            let myCenter = this.getCenter();
            let nextCenter = tiles[this.index + this.snadder].getCenter();
            strokeWeight(4);
            if(this.snadder <0)
                stroke(255,0,0);
            else
                stroke(255);
            line(myCenter[0],myCenter[1],nextCenter[0],nextCenter[1]);
        }
    }
}
