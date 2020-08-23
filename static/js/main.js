window.addEventListener('load', init);


class AlternateTitle{
    constructor(position, title){
        this.position = position;
        this.title = title.replace(')', '').trim();
    }
}

//Globals
let timelimit = 120;
time = timelimit;
let score = 0;
let isPlaying;
let includesParenthesis;
let randomString = "RandomStringq23487r8hfaoifh219035y0roiwasdfhasdfkljhsfakjlkRandomString";
// DOM Elements
const songInput = document.querySelector('#word-input');
const tracklistDisplay = document.querySelector('#track-list-guesses');
const scoreDisplay = document.querySelector('#score');
const timeDisplay = document.querySelector('#time');
const message = document.querySelector('#message');
const seconds = document.querySelector('#seconds');
const title = document.querySelector('#album-title');
const timeString = document.querySelector('#instructions-time');

answersButton = document.getElementById("answers_button");
giveUpButton = document.getElementById("giveup-button");
resetButton = document.getElementById("reset-button");
discString = document.getElementById("disc_string").value;
trackString = document.getElementById("track_list").value;
artist = document.getElementById("artist").value;
album = document.getElementById("album-name").value;
/* albumID = document.getElementById("album-id");
csrf = document.getElementById("csrf-token").value;
albumContainer = document.getElementById("album-container"); */
instructions = document.getElementById("instructions-panel");
cheatMessage = document.getElementById("album-creator");
uiPanel = document.getElementById("ui-panel");

socialPanel = document.getElementById("social-panel");
facebookButton = document.getElementById("facebook-button");
twitterButton = document.getElementById("twitter-button");
tumblrButton = document.getElementById("tumblr-button");
redditButton = document.getElementById("reddit-button");
emailButton = document.getElementById("email-button");
pinterestButton = document.getElementById("pinterest-button");

fixedString = unicodeToChar(trackString.replace('[', '').replace(']', '')).substr(1).replace(/‘/g, '\'').replace(/’/g, '\'').replace(/‐/g,'-').replace(/…/g,'...');
var tracks = fixedString.substring(0, fixedString.length - 1).split("\"\, \"", );


var trackGuesses = new Array();
var discTrackNumbers = new Array();
if(discString.substring(0,1) > 1){
    discTrackNumbers = discString.split("X");
}
//console.log(trackGuesses);
//check for parenthesis (alternate titles). Creates separate entites to check and stores track number.
alternateTitles = new Array();
for(i = 0; i< tracks.length; i++){
    if(tracks[i].includes('(')){
        splitTracks = tracks[i].split('(');
        for(h=0; h<splitTracks.length; h++){
            if(!(splitTracks[h].toLowerCase().startsWith('feat') || splitTracks[h].toLowerCase().startsWith('reprise') 
                || splitTracks[h].toLowerCase().startsWith('intro') || splitTracks[h].toLowerCase().startsWith('instrumental'))){ //only want alternate titles, not features.
                if(splitTracks[h].length > 1){
                    alternateTitles[alternateTitles.length] = new AlternateTitle(i, splitTracks[h]);
                    includesParenthesis = true;
                }
            }
        }
    }
    if(tracks[i].includes('/')){
        splitTracks = tracks[i].split('/');
        for(h=0; h<splitTracks.length; h++){
            alternateTitles[alternateTitles.length] = new AlternateTitle(i, splitTracks[h]);
            includesParenthesis = true;
            if(splitTracks[h].includes('&')){
                alternateTitles[alternateTitles.length] = new AlternateTitle(i, splitTracks[h].replace(/&/g, ' and ').replace(/\'  \'/g, ' '));
            }
        }
    }
    if(tracks[i].includes('&')){
        alternateTitles[alternateTitles.length] = new AlternateTitle(i, tracks[i].replace(/&/g, ' and ').replace(/\'  \'/g, ' '));
        includesParenthesis = true;
    }
}

originalTracks = tracks.slice(0); //store Arrays for reset
originalAltTitles = alternateTitles.slice(0);

finalResultString = "";
finishTime = 0;
ranOnceAtGameOver = false;
answersVisable = false;

//console.log(originalTracks); 
//console.log(originalAltTitles);

// Initialise Game
function init() {
    timelimit = tracks.length * 8;
    time = tracks.length * 8;

    answersButton.style.display = "none";
    uiPanel.style.display = "none";
    songInput.style.display = "none";
    songInput.value = '';
    timeString.innerHTML = timeConverter(time);
    displayHiddenTracks();
    if(artist == 'Unknown'){
        cheatMessage.innerHTML = album + '\'s creator';
    } else if(artist == 'Various Artists' || artist == null){
        cheatMessage.innerHTML = 'the creators of ' + album;
    }
    else{
        cheatMessage.innerHTML = artist;
    }
    instructions.scrollIntoView();
    songInput.addEventListener('input', startMatch);
    setInterval(countdown, 1000);
    setInterval(checkStatus, 50);
}

function timeConverter(seconds){
    mPad = "";
    sPad = "";
    min = Math.floor(seconds/60);
    sec = seconds%60;
    if(sec<10){
        sPad = "0";
    }
    if(min > 0){
/*      if(min<10){             m pad looks ugly
            mPad = "0";
        } */
        return mPad + min +"m" + sPad + sec +"s";
    } 
    else{
        return sPad + sec +"s";
    }
}

function goToGame(){
    uiPanel.style.display = "block";
    songInput.style.display = "block";
    songInput.focus();
    instructions.style.display = "none";
    timeDisplay.innerHTML  = "TIME: " + timeConverter(time);
    giveUpButton.scrollIntoView();
}

function startMatch(){
    isPlaying = true;
    if(matchWords()){
        songInput.value = '';
        score++;
        var ofs = 0;
        flashGreen = setInterval(function(){
            change = Math.abs(Math.sin(ofs));
            rvalue = Math.floor(255-200*change);
            gvalue = Math.floor(255-80*change);
            bvalue = Math.floor(255-200*change);
            songInput.style.background = 'rgba('+ rvalue +','+gvalue+','+bvalue+',1)';
            ofs += 0.03;
            if(ofs > 3.1415){
                clearInterval(flashGreen);
            }
         }, .1);
    }
    scoreDisplay.innerHTML = score;
}

function matchWords(){
    songInput.addEventListener('keyup', function(e){
        if(e.key === "Enter"){
            if(songInput.value != ''){
                var ofs = 0;
                flashRed = setInterval(function(){
                    change = Math.abs(Math.sin(ofs));
                    rvalue = Math.floor(255-40*change);
                    gvalue = Math.floor(255-200*change);
                    bvalue = Math.floor(255-200*change);
                    songInput.style.background = 'rgba('+ rvalue +','+gvalue+','+bvalue+',1)';
                    ofs += 0.03;
                    if(ofs > 3.1415){
                        clearInterval(flashRed);
                    }
                 }, .1);
            }
            songInput.value = '';
        }
    });
    normailzedInput = strip(songInput.value.normalize('NFD').replace(/[\u0300-\u036f]/g, "").toLowerCase().trim());
    var songIndex = tracks.findIndex(item => normailzedInput === strip(item.normalize('NFD').replace(/[\u0300-\u036f]/g, "").toLowerCase()));

    if(songIndex > -1){ //if there's a match in the main set
        tracklistDisplay.innerHTML = updateDisplay(songIndex);

        //marks songs as found in standard list and removes from alt list
        tracks[songIndex] = randomString;
        for(h=0;h<alternateTitles.length;h++){
            if(alternateTitles[h].position == songIndex){
                alternateTitles.splice(h,1);
                h--;
            }
        }
        return true;
    } else{
        if(includesParenthesis){ //check for matches in alternate title set
            for(i=0;i<alternateTitles.length;i++){
                if(strip(alternateTitles[i].title.normalize('NFD').replace(/[\u0300-\u036f]/g, "").toLowerCase()) == normailzedInput){
                    index = alternateTitles[i].position;
                    tracklistDisplay.innerHTML = updateDisplay(index);

                    //remove match from main and alternate sets
                    tracks[index] = randomString;
                    for(h=0;h<alternateTitles.length;h++){
                        if(alternateTitles[h].position == index){
                            alternateTitles.splice(h,1);
                            h--;
                        }
                    }
                    return true;
                }
            }
        }
        message.innerHTML = '';
        return false;
    }
}

function updateDisplay(index){
    discIndex = 0;
    trackIndex = 0;
    display = "";
    for(i=0;i<tracks.length;i++){
        trackIndex++;
        if(discTrackNumbers[0] > 1){
            if(trackIndex == 1){
                discIndex++;
                if(discIndex > 1){
                    display += "<br>"
                }
                display += "DISC "+ discIndex + "<br>";
            }
        }
        if(i==index){
            trackGuesses[i] = "<span style=\"color:salmon\">" + "<b>" + trackIndex +".&nbsp;" + "</b>"+ "</span>" + tracks[i].replace(/ /g,"&nbsp;");
        }
        display += trackGuesses[i] + " ";
        if(trackIndex == discTrackNumbers[discIndex]){
            trackIndex = 0;
        }
    }
    return display;
}

function giveUp(){
    time = 0;
    timeDisplay.innerHTML = time;
    isPlaying = false;
}

function reset(){
    tracks = originalTracks.slice(0);
    alternateTitles = originalAltTitles.slice(0);
    score = 0;
    scoreDisplay.innerHTML = score;
    time = timelimit;
    timeDisplay.innerHTML = "TIME: " + timeConverter(time);
    songInput.value = '';
    songInput.focus();
    songInput.style.display = "block";
    answersButton.style.display = "none";
    socialPanel.style.display = "none";
    giveUpButton.style.display = "inline-block";
    message.innerHTML = "";
    displayHiddenTracks();
    isPlaying = false;
    ranOnceAtGameOver = false;
    songInput.addEventListener('input', startMatch);

}

function showMissedTracks(){
    if(answersVisable){
        tracklistDisplay.innerHTML = finalResultString;
        answersVisable = false;
    }
    else{
        answersVisable = true;
        discIndex = 0;
        trackIndex = 0;
        tracklistDisplay.innerHTML = "";
        for(i=0;i<tracks.length;i++){
            trackIndex++;
            if(discTrackNumbers[0] > 1){
                if(trackIndex == 1){
                    discIndex++;
                    if(discIndex > 1){
                        tracklistDisplay.innerHTML += "<br>"
                    }
                    tracklistDisplay.innerHTML += "DISC "+ discIndex + "<br>";
                }
            }
            if(tracks[i]==randomString){
                trackGuesses[i] = "<span style=\"color:salmon\">" + "<b>"+trackIndex +".&nbsp;" + "</b>"+ "</span>" + originalTracks[i].replace(/ /g,"&nbsp;");
            }
            else{
                trackGuesses[i] = "<span style=\"color:salmon\">" + "<b>"+trackIndex +".&nbsp;" + "</b>"+ "</span>" + "<span style=\"color:#f0ad4e\">" + originalTracks[i].replace(/ /g,"&nbsp;") + "</span>";
                
            }
            tracklistDisplay.innerHTML += trackGuesses[i] + " ";
            if(trackIndex == discTrackNumbers[discIndex]){
                trackIndex = 0;
            }
        }
    }
}

function displayHiddenTracks(){
    discIndex = 0;
    trackIndex = 0;
    tracklistDisplay.innerHTML = "";
    for(i=0;i<tracks.length;i++){
        trackIndex++;
        if(discTrackNumbers[0] > 1){
            if(trackIndex == 1){
                discIndex++;
                if(discIndex > 1){
                    tracklistDisplay.innerHTML += "<br>"
                }
                tracklistDisplay.innerHTML += "DISC " + discIndex + "<br>";
            }
        }
        trackGuesses[i] = "<span style=\"color:salmon\">" + "<b>"+trackIndex +"." +"</b>" + "</span>"+ "_".repeat(tracks[i].length+3);
        tracklistDisplay.innerHTML += trackGuesses[i] + " ";
        if(trackIndex == discTrackNumbers[discIndex]){
            trackIndex = 0;
        }
    }
}

function countdown() {
    if(time > 0 && isPlaying){
        time--;
        timeDisplay.innerHTML  = "TIME: " + timeConverter(time);
    } else if(time === 0){
        isPlaying = false;
        timeDisplay.innerHTML  = "TIME UP";
    }
}

function checkStatus(){
    if(isPlaying && score == tracks.length){
        finishTime = time;
        isPlaying = false;
        songInput.style.display = "none";
        message.innerHTML = 'You got them all with ' + time + ' seconds to spare!';
        giveUpButton.style.display = "none";
        setSocialLinks(true);
        answersButton.style.display = "none";
        resetButton.scrollIntoView();
        socialPanel.style.display = "block";
    }
    if(!isPlaying && time === 0){
        isPlaying = false;
        message.innerHTML = 'You got ' + score + ' out of ' + tracks.length + '!';
        songInput.style.display = "none";
        setSocialLinks(false);
        socialPanel.style.display = "block";
        if(!ranOnceAtGameOver){
            finalResultString = updateDisplay(-1);
            answersButton.scrollIntoView();
            ranOnceAtGameOver = true;
        }
        answersButton.style.display = "inline-block";
        giveUpButton.style.display = "none";
        timeDisplay.innerHTML  = "TIME UP";
    }
}

function setSocialLinks(gotThemAll){
    if(gotThemAll){
        timeTaken = timeConverter(tracks.length*8-time);
        shareMessage = ("I got them all in " + timeTaken +'!').replace(' ','%20');
    }
    else{
        shareMessage = ("I got " + score + ' out of ' + tracks.length + '!').replace(' ','%20');
    }

    if(artist == 'Unknown' || artist == 'Various Artists' || artist == null){
        shareTitle = ('The ' + album + ' Tracklist Challenge').replace(' ','%20');
        longerMessage = ("How many tracks from " + album + " can you list? " + shareMessage).replace(' ','%20');
    }
    else{
        shareTitle = (artist+'\'s \''  + album + '\' Tracklist Challenge').replace(' ','%20');
        longerMessage = ("How many tracks from " +artist+'\'s \''  + album + "\' can you list? " + shareMessage).replace(' ','%20');
    }

    twitterButton.href = "https://twitter.com/intent/tweet/?text="+shareMessage+"&url=" + window.location.href;
    facebookButton.href = "https://www.facebook.com/sharer/sharer.php?u="+window.location.href+"&quote="+shareMessage;
    redditButton.href = "https://reddit.com/submit/?url="+window.location.href+"&resubmit=true&title="+longerMessage;
    tumblrButton.href = "https://www.tumblr.com/widgets/share/tool?posttype=link&title="+shareTitle+"&caption="+ longerMessage +"&content="+window.location.href+"&canonicalUrl="+window.location.protocol+'//'+window.location.hostname+"&shareSource=tumblr_share_button";
    //pinterestButton.href = "https://pinterest.com/pin/create/button/?url="+window.location.href+"&media="+window.location.href+"&description="+longerMessage;
    emailButton.href = "mailto:?subject="+shareTitle+"&body="+longerMessage;
}

function unicodeToChar(text) {
    return text.replace(/\\u[\dA-F]{4}/gi, 
           function (match) {
                return String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16));
           });
 }

function stripThe(phrase){
    if(phrase.toLowerCase().startsWith('the ')){
        return phrase.substring(4);
    }
    else{
        return phrase
    }
}

function stripPunctuation(phrase){
    punctuationless1 = phrase.replace(/-/g," ");
    punctuationless = punctuationless1.replace(/[.…,\/#!?’‘”″“$%\^&\*;:'{}=\‐_`~()]/g,"");
    return punctuationless.replace(/\s{2,}/g," ");
}

function strip(phrase){
    return stripThe(stripPunctuation(phrase))
}
