package ChatServer;

import ChatServer.Endpoints.AccountsEndpointSession;
import java.util.ArrayList;
import java.util.List;

public class ConnectionsHandler {
    public List<AccountsEndpointSession> connectedClients;
    public int numConnectedClients;

    public ConnectionsHandler() {
        connectedClients = new ArrayList<AccountsEndpointSession>();
        numConnectedClients = 0;
    }

    public void AddClient(AccountsEndpointSession account) {
        connectedClients.add(account);
        numConnectedClients++;
    }

    public void MessageAll(String message) {
        for (AccountsEndpointSession account: connectedClients) {
            account.messageSelf(message);
        }
    }
}
