package ChatServer.Endpoints;

import java.io.IOException;

import javax.websocket.OnClose;
import javax.websocket.OnMessage;
import javax.websocket.OnOpen;
import javax.websocket.Session;
import javax.websocket.server.ServerEndpoint;

import ChatServer.ChatServer;
import ChatServer.ConnectionsHandler;

/**
 * @ServerEndpoint gives the relative name for the end point
 * This will be accessed via ws://localhost:8080/auth_war_exploded/chat
 * Where "localhost" is the address of the host,
 * "auth_war_exploded" is the name of the artifact
 * and "accounts" is the address to access this class from the connectionsHandler
 */
@ServerEndpoint("/chat")
public class ChatEndpointSession {

    private String aid;
    String username;
    Session session;
    ConnectionsHandler connectionsHandler;

    private void link() {
        messageSelf("1");
        messageSelf(Integer.toString(ChatServer.connectionsHandler.numConnectedClients));
        ChatServer.connectionsHandler.AddClient(this);
        messageSelf(Integer.toString(ChatServer.connectionsHandler.numConnectedClients));
        messageSelf("2");
    }

    public void messageSelf(String message) {
        privateMessage(message, session);
    }

    public void privateMessage(String message, Session peer) {
        try {
            peer.getBasicRemote().sendText(message);
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }

    public void publicMessage(String message) {
        for (Session peer: session.getOpenSessions()) {
            privateMessage(username + ": " + message, peer);
        }
    }

    private void setUsername(String newUsername) {
        this.username = newUsername;
    }

    private boolean usernameHasBeenSet() {
        return !(username.equals("unknown"));
    }

    private void giveGreeting() {
        messageSelf(String.format("Welcome %s", username));
    }

    private void announceEntry() {
        publicMessage(String.format("Welcome %s to the channel", username));
    }

    /**
     * @OnOpen allows us to intercept the creation of a new session.
     * The session class allows us to send data to the user.
     * In the method onOpen, we'll let the user know that the handshake was
     * successful.
     */
    @OnOpen
    public void onOpen(Session session){
        connectionsHandler = ChatServer.connectionsHandler;
        setUsername("unknown");
        this.session = session;
        messageSelf("Established Connection.");
        messageSelf("Please send over your desired Username");
    }

    /**
     * When a user sends a message to the connectionsHandler, this method will intercept the message
     * and allow us to react to it. For now the message is read as a String.
     */
    @OnMessage
    public void onMessage(String message, Session session){
        if (usernameHasBeenSet()) {
            publicMessage(message);
        } else {
            setUsername(message);
            giveGreeting();
            announceEntry();
        }
    }

    /**
     * The user closes the connection.
     *
     * Note: you can't send messages to the client from this method
     */
    @OnClose
    public void onClose(Session session){
        System.out.println("Session " +session.getId()+" has ended");
    }
}
