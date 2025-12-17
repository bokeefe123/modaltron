/**
 * SocketClient
 */
function SocketClient() {
    this.id = null;
    this.connected = false;

    this.onError = this.onError.bind(this);
    this.onOpen = this.onOpen.bind(this);
    this.onConnection = this.onConnection.bind(this);
    this.onPing = this.onPing.bind(this);

    var Socket = window.MozWebSocket || window.WebSocket;

    var protocol = 'ws://';
    if (location.protocol === 'https:') {
        protocol = 'wss://';
    }

    BaseSocketClient.call(this, new Socket(protocol + document.location.host + document.location.pathname, ['websocket']));

    this.socket.addEventListener('open', this.onOpen);
    this.socket.addEventListener('error', this.onError);
    this.socket.addEventListener('close', this.onClose);

    // Handle server ping requests for latency measurement
    this.on('ping', this.onPing);
}

SocketClient.prototype = Object.create(BaseSocketClient.prototype);
SocketClient.prototype.constructor = SocketClient;

/**
 * On socket connection
 *
 * @param {Socket} socket
 */
SocketClient.prototype.onOpen = function (e) {
    console.info('Socket open.');
    this.addEvent('whoami', null, this.onConnection);
};

/**
 * On open
 *
 * @param {Event} e
 */
SocketClient.prototype.onConnection = function (id) {
    console.info('Connected with id "%s".', id);

    this.id = id;
    this.connected = true;

    this.start();
    this.emit('connected');
};

/**
 * On open
 *
 * @param {Event} e
 */
SocketClient.prototype.onClose = function (e) {
    console.info('Disconnected.');

    this.connected = false;
    this.id = null;

    this.stop();

    this.emit('disconnected');
};

/**
 * On error
 *
 * @param {Event} e
 */
SocketClient.prototype.onError = function (e) {
    console.error(e);

    if (!this.connected) {
        this.onClose();
    }
};

/**
 * On ping - respond with pong for latency measurement
 *
 * @param {Number|Object} data
 */
SocketClient.prototype.onPing = function (data) {
    // Handle both direct value and EventEmitter wrapper
    var timestamp = (typeof data === 'object' && data !== null) ? data.detail : data;
    console.log('Responding to ping with timestamp:', timestamp);
    this.addEvent('pong', timestamp, null, true);
};
