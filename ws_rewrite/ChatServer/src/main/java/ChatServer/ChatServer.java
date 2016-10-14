package ChatServer;

public class ChatServer {

    public static ConnectionsHandler connectionsHandler;

    public static void main(String[] args) {
        connectionsHandler = new ConnectionsHandler();
    }
}
