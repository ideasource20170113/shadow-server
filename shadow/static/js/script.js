$(document).ready(function () {
    const socket = io('/web');
    const ENTER = 13;
    const KEY_UP = 38;
    const KEY_DOWN = 40;
    const $join = $('#join-room');
    const $pre = $('.terminal-text pre');
    const $input = $('.console-input');
    const $label = $('.jquery-console-prompt-label');
    const $clear = $('#clearTerminal');

    socket.on('connect', function () {
        socket.emit('joined', {
            'agent_id': $label.attr('id')
        });
        socket.emit('joined', {
            'agent_id': $('.monitor-desktop').attr('id')
        });
        socket.emit('monitor', {
            'room': $('.monitor-desktop').attr('id')
        });
    });

    socket.on('command', function (data) {
        $pre.append(data);
        $('html,body').animate({scrollTop: $input.offset().top}, 800);
    });

    socket.on('status', function (data) {
        $join.append('&lt;' + data.msg + '&gt;');
    });

    socket.on('upload', function (data) {
        $('.terminal-text').append(data);
    });

    socket.on('monitor', function (data) {
        console.log(data);
        data = 'data:image/png;base64,' + data;
        $('.monitor-desktop').attr('src', data);
    });

    $(window).on('beforeunload', function () {
        socket.emit('left', {
            'agent_id': $label.attr('id')
        });
        window.location.href = "{{ url_for('agent.home') }}";
    });

    $input.keydown(function (e) {
        onCommandKeypressedAction(e);
    });

    function onCommandKeypressedAction(e) {

        if (e.keyCode === ENTER) { // ENTER
            console.log('enter');
            const command = $input.val();
            console.log(command);
            if (command) {
                if (command === 'clear') {
                    $pre.empty();
                } else if (command === 'exit') {
                    history.back(-1);
                } else {
                    sendCommand();
                }
            }
            $input.val('');
        } else if (e.keyCode === KEY_UP) { // KEY_UP
            console.log('up');
            sendCommand();
        } else if (e.keyCode === KEY_DOWN) { // KEY_DOWN
            console.log('down');
        }

        return false;
    }

    function sendCommand() {
        window.console.log('发送消息');
        socket.emit('command',
            {
                'agent_id': $label.attr('id'),
                'command': $input.val(),
            });
        $input.val('');
    }

    $clear.on('click', function () {
        $pre.empty();
    });

    function activateSemantics() {
        $('.ui.dropdown').dropdown();
        $('.ui.checkbox').checkbox();


        $('#toggle-sidebar').on('click', function () {
            $('.menu.sidebar').sidebar('setting', 'transition', 'overlay').sidebar('toggle');
        });

        $('#show-help-modal').on('click', function () {
            $('.ui.modal.help').modal({blurring: true}).modal('show');
        });

        $('#show-snippet-modal').on('click', function () {
            $('.ui.modal.snippet').modal({blurring: true}).modal('show');
        });

        $('.pop-card').popup({
            inline: true,
            on: 'hover',
            hoverable: true,
            html: popupLoading,
            delay: {
                show: 200,
                hide: 200
            },
            onShow: function () {
                var popup = this;
                popup.html(popupLoading);
                $.get({
                    url: $(popup).prev().data('href')
                }).done(function (data) {
                    popup.html(data);
                }).fail(function () {
                    popup.html('Failed to load profile.');
                });
            }
        });
    }

    function init() {
        // desktop notification
        document.addEventListener('DOMContentLoaded', function () {
            if (!Notification) {
                alert('Desktop notifications not available in your browser.');
                return;
            }

            if (Notification.permission !== "granted")
                Notification.requestPermission();
        });

        $(window).focus(function () {
            document.title = 'Shadow';
        });

        activateSemantics();
        scrollToBottom();
    }

    init();
});


