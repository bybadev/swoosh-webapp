var socket;
$(document).ready(function(){
    //socket = io.connect('https://' + document.domain + ':' + location.port + '/chat');
    //socket = io.connect('https://' + 'swooshchat.herokuapp.com' + ':' + location.port + '/chat');
    socket = io.connect(document.domain + ':' + location.port + '/chat');
    socket.on('connect', function() {
        socket.emit('joined', {});
    });

    socket.on('status', function(data) {
        $('#chat').val($('#chat').val() + '<' + data.msg + '>\n');
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });

    socket.on('message', function(data) {
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
        document.getElementById("chat").innerHTML = $('#chat').val($('#chat').val() + data.msg + '\n');
    });
    $('#text').keypress(function(e) {
        var code = e.keyCode || e.which;
        if (code == 13) {
            text = $('#text').val();        
            $('#text').val('');
            socket.emit('text', {msg: text});
        }
    });
});

function leave_room() {
    socket.emit('left', {}, function() {
        socket.disconnect();
    });
}