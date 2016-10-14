package ChatServer;

import ChatServer.Endpoints.ChatEndpointSession;
import java.util.ArrayList;
import java.util.List;

public class ConnectionsHandler {
    public List<ChatEndpointSession> connectedClients;
    public int numConnectedClients;

    public ConnectionsHandler() {
        connectedClients = new ArrayList<ChatEndpointSession>();
        numConnectedClients = 0;
    }

    public void AddClient(ChatEndpointSession account) {
        connectedClients.add(account);
        numConnectedClients++;
    }

    public void MessageAll(String message) {
        for (ChatEndpointSession account: connectedClients) {
            account.messageSelf(message);
        }
    }
}
