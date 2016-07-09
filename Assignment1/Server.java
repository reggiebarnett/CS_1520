import java.net.Socket;
import java.net.ServerSocket;
import java.io.*;

public class Server {

  public static void main(String[] arguments) throws Exception {

    ServerSocket serverSocket = new ServerSocket(8080);
    Socket clientConnection = null;
	
    do {
      clientConnection = serverSocket.accept();
      
      InputStream in = clientConnection.getInputStream();
      BufferedReader reader = new BufferedReader(new InputStreamReader(in));
      String line = reader.readLine();
	  HTTPRequest HTTPReq = new HTTPRequest(clientConnection,line,reader);
    } while (clientConnection != null);
  }
}