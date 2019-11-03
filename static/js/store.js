function buyPerk(perkArr){
    console.log(perkArr)
    if(perkArr[1]<=availableGold){
        availableGold -= perkArr[1];
        arr=['perkBought',perkArr[0],availableGold]
        socket_private.emit('buyPerk', arr);
        document.getElementById('availableGold').innerHTML = availableGold;
        document.getElementById('perkPassAlert').hidden = false;
        document.getElementById('perkFailAlert').hidden = true;
    }
    else{
        document.getElementById('perkPassAlert').hidden = true;
        document.getElementById('perkFailAlert').hidden = false;
    }
}