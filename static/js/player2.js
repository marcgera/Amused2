var g_playListItemsVideo;
var g_playListItemsMusic;
var g_PreviousCategory;
var g_PlayListMusicForCategory;
var g_VideoDuration1 = 9999;
var g_VideoDuration2 = 9999;
var g_fadeTime;
var g_currentPlaylistItemVideo;
var g_currentPlaylistVideoItemIndex = 0;
var g_currentPlaylistMusicItemIndex = 0;
var g_CurrentMusicPlayList;
var g_VideoTimePassed1 = 0;
var g_VideoTimePassed2 = 0;
var g_playingVideo1 =1 ;
var g_playingAudio1 =1 ;
var g_fadeTime = 6000;
var g_FadeTimerInterval = 200;
var g_TransitionUngoing = false;
var g_FadeDelta;
var g_PlayedMusic =[];
var video_loc = "https://storage.cloud.google.com/amused_media/media/video/";
var music_loc = "https://storage.cloud.google.com/amused_media/media/music/";


g_audioElement1 = document.createElement('audio');
g_audioElement2 = document.createElement('audio');
g_audioElement1.volume = 1;
g_audioElement2.volume = 1;
var g_video1 = $('#video1')[0];
var g_video2 = $('#video2')[0];

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);

$(document).ready(function () {

    g_video1 = $('#video1')[0];
    g_video2 = $('#video2')[0];


    g_FadeDelta = g_FadeTimerInterval / g_fadeTime;

    params = "?playlist_ID=" + urlParams.get('playlist_ID');

    $.get("/getPlaylistItemsVideo" + params, function (data, status) {
        g_playListItemsVideo = JSON.parse(data);
        preLoadMedia();
    });

    $.get("/getPlaylistItemsMusic" + params, function (data, status) {
        g_playListItemsMusic = JSON.parse(data);
        preLoadMedia();
    });

    g_video1.addEventListener('loadedmetadata', function () {
        g_VideoDuration1 = g_video1.duration.toFixed(2);
        updateDurationDiv();
    }, false);

    g_video2.addEventListener('loadedmetadata', function () {
        g_VideoDuration2 = g_video2.duration.toFixed(2);
        updateDurationDiv();
    }, false);

    g_video1.addEventListener('ended', function () {
        playNextVideo();
    }, false);

    g_video2.addEventListener('ended', function () {
        playNextVideo();
    }, false);

    g_audioElement1.addEventListener('ended', function () {
        playNextMusic();
    }, false);

    g_audioElement2.addEventListener('ended', function () {
        playNextMusic();
    }, false);

    g_video1.addEventListener("timeupdate", function () {
        g_VideoTimePassed1 = g_video1.currentTime.toFixed(2);
        ilv = IsLastVideoInCategory();
        condition =  ilv &&  g_video1.currentTime > g_VideoDuration1 - g_fadeTime/1000 && !g_TransitionUngoing
        if (condition) {
            g_TransitionUngoing = true;
            g_fadeVolume = 1;
        }
        updateVideoTimePassedDiv();
    });

    g_video2.addEventListener("timeupdate", function () {
        g_VideoTimePassed2 = g_video2.currentTime.toFixed(2);
        if (IsLastVideoInCategory() &&  g_video2.currentTime > g_VideoDuration2 - g_fadeTime/1000 && !g_TransitionUngoing) {
            g_TransitionUngoing = true;
            g_fadeVolume = 1;
        }
        updateVideoTimePassedDiv();
    });

    $('#play').on('click', function () {
        doPlay();
    })
    
    $('#stop').on('click', function () {
        doStop();
    })

    setTimeout(function() {
        doPlay();
      }, 5000);

    tmr = setInterval(() => {
        if (!g_TransitionUngoing) {return}
        $("#currentVolume2").text('Fadevolume:' + g_fadeVolume.toString());
        currentAudio = getCurrentAudioElement();
        currentAudio.volume = g_fadeVolume;
        g_fadeVolume = g_fadeVolume-g_FadeDelta;
    
        if (g_fadeVolume<.1){
            g_TransitionUngoing = false;
            currentAudio.pause();
            g_fadeVolume = 1;
            g_audioElement1.volume = 1;
            g_audioElement2.volume = 1;
        }
    
    }, g_FadeTimerInterval);
});

function IsLastVideoInCategory(){

    if (g_currentPlaylistVideoItemIndex == g_playListItemsVideo.length -1){
        return true;
    }

    thisVideo = g_playListItemsVideo[g_currentPlaylistVideoItemIndex];
    nextVideo = g_playListItemsVideo[g_currentPlaylistVideoItemIndex+1];

    if (thisVideo.videos_category_SO == nextVideo.videos_category_SO){
        return false;
    }
    else {
        return true;
    }
}

function getCurrentAudioElement() {
    if (g_playingAudio1) {
        $("#currentAudio").text('currentAudio: 1');
        return g_audioElement1;
    }
    else {
        $("#currentAudio").text('currentAudio: 2');
        return g_audioElement2;
    }
}

function updateDurationDiv(){
    dur = 'VideoDuration: ';
    dur = dur.concat( g_VideoDuration1.toString() , ' - ' , g_VideoDuration2.toString()); 
    vd = $('#videoDuration')[0];
    vd.innerHTML  = dur;
}

function updateVideoTimePassedDiv(){
    dur = 'Video Time passed: ';
    dur = dur.concat( g_VideoTimePassed1.toString() , ' - ' , g_VideoTimePassed2.toString()); 
    vd = $('#videoTimePassed')[0];
    vd.innerHTML  = dur;
}

function doPlay() {
    g_video1.play();
    plItem = g_playListItemsVideo[0];
    logVideo(plItem);
    g_audioElement1.play();
    plitem = g_playListItemsMusic[0];
    logMusic(plitem);
}

function doStop() {
    g_audioElement1.pause();
    g_audioElement2.pause();
    g_video1.pause();
    g_video2.pause();
}

function loadPlayListMusic(video_category_SO){
    g_currentPlaylistMusicItemIndex = 0;
    p_PlayListMusicForCategory=[];
    g_playListItemsMusic.forEach(function (item, index) {
        if (item.music_category_SO == video_category_SO){
            p_PlayListMusicForCategory.push(item);
        }
      }); 
    return(p_PlayListMusicForCategory);
}

function preLoadMedia() {
    if (g_playListItemsVideo && g_playListItemsMusic) {
        g_currentPlaylistItemVideo = 0;
        g_playing1 = true;
        g_currentPlaylistMusicItemIndex = 0;
        plItemVideo = g_playListItemsVideo[0];
        g_PreviousCategory = plItemVideo.videos_category_SO;
        g_CurrentMusicPlayList = loadPlayListMusic(plItemVideo.videos_category_SO);
        plItemMusic = g_CurrentMusicPlayList[0]
        
        srcVideo = video_loc + plItemVideo.backgrounds_name + '/' + plItemVideo.videos_name;
        srcAudio = music_loc + plItemMusic.music_filename;

        g_audioElement1.setAttribute('src', srcAudio);
        g_video1.setAttribute('src', srcVideo);

        g_PlayedMusic.push(plItemMusic.ID);

        if (g_playListItemsVideo.length > 1) {
            plItemVideo = g_playListItemsVideo[1];
            srcVideo = '../static/video/' + plItemVideo.backgrounds_name + '/' + plItemVideo.videos_name;
            g_video2.setAttribute('src', srcVideo);
        }

        if (g_CurrentMusicPlayList.length > 1) {
            g_currentPlaylistMusicItemIndex = g_currentPlaylistMusicItemIndex + 1;
            plItemMusic = g_CurrentMusicPlayList[g_currentPlaylistMusicItemIndex];
            srcAudio = '../static/music/' + plItemMusic.music_filename;
            g_audioElement2.setAttribute('src', srcAudio);
        }

        g_video1.volume = 0;
        g_video2.volume = 0;
        g_video1.style.opacity = '1';
        g_video2.style.opacity = '0';
    }
}

function playNextMusic(){
    if (g_currentPlaylistMusicItemIndex == g_CurrentMusicPlayList.length - 1) {
        g_currentPlaylistMusicItemIndex = 0;
    }
    else {
        g_currentPlaylistMusicItemIndex = g_currentPlaylistMusicItemIndex + 1;
    }
    plItemMusic = g_CurrentMusicPlayList[g_currentPlaylistMusicItemIndex];
    srcAudio = '../static/music/' + plItemMusic.music_filename;
    g_PlayedMusic.push(plItemMusic.ID);

    if (g_playingAudio1) {
        g_audioElement1.pause();
        g_audioElement2.play();
        g_audioElement1.setAttribute('src',srcAudio);
        g_playingAudio1 = 0;
    }
    else {
        g_audioElement2.pause();
        g_audioElement1.play();
        g_audioElement2.setAttribute('src',srcAudio);
        g_playingAudio1 = 1;
    }
    logMusic(plItemMusic);
}

function playNextVideo() {
    g_TransitionUngoing = false;
    if (g_currentPlaylistVideoItemIndex == g_playListItemsVideo.length - 1) {
        doStop();
        return
    }
    else {
        g_currentPlaylistVideoItemIndex = g_currentPlaylistVideoItemIndex + 1;
    }

    plItemVideo = g_playListItemsVideo[g_currentPlaylistVideoItemIndex];
    srcVideo = '../static/video/' + plItemVideo.backgrounds_name + '/' + plItemVideo.videos_name;
    p_CurrentCategory = plItemVideo.videos_category_SO;

    if (g_PreviousCategory !== p_CurrentCategory){
        g_PreviousCategory = p_CurrentCategory;
        g_audioElement1.pause;
        g_audioElement2.pause;
        g_playingAudio1 = 1;
        g_CurrentMusicPlayList = loadPlayListMusic(p_CurrentCategory);
        plItemMusic = g_CurrentMusicPlayList[0];
        srcAudio = '../static/music/' + plItemMusic.music_filename;
        g_PlayedMusic.push(plItemMusic.ID);
        g_audioElement1.setAttribute('src', srcAudio);
        g_currentPlaylistMusicItemIndex = 0;
        if (g_CurrentMusicPlayList.length > 1) {
            plItemMusic = g_CurrentMusicPlayList[1];
            srcAudio = '../static/music/' + plItemMusic.music_filename;
            g_audioElement2.setAttribute('src', srcAudio);
            g_currentPlaylistMusicItemIndex = 1;
        }

        g_audioElement1.play();
    }

    if (g_playingVideo1) {
        previousVideoElement = g_video1;
        videoElement = g_video2;
        g_playingVideo1 = false;
    }
    else {
        previousVideoElement = g_video2;
        videoElement = g_video1;
        g_playingVideo1 = true;
    }


    videoElement.style.opacity = 1;
    previousVideoElement.style.opacity = 0;
    videoElement.setAttribute('src', srcVideo);
    videoElement.play();
    logVideo(plItemVideo);
}

function logVideo(plItemVideo){
    params = "?video_ID=" + plItemVideo.playlist_videos_video_ID;
    params = params + "&background_ID=" + plItemVideo.backgrounds_sort_order;
    params = params + "&playlist_ID=" + plItemVideo.playlist_videos_playlist_ID;

    $.get("/logVideo" + params, function (data, status) {
    });
}

function logMusic(plItemMusic){
    params = "?music_ID=" + plItemMusic.playlist_music_music_ID;
    params = params + "&playlist_ID=" + plItemMusic.playlist_music_playlist_ID;

    $.get("/logMusic" + params, function (data, status) {
    });
}





