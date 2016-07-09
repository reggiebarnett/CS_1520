//Reggie Barnett
//CS 1520
//HTTP Request

import java.net.Socket;
import java.io.*;

public class HTTPRequest{

	String delims = "[ /?=&]+";
	//Processing initial request
	HTTPRequest(Socket clientConnection, String line,BufferedReader reader) throws Exception{
		//Checking for type of request
		String[] RequestType = line.split(delims);
		//If GET then continue, otherwise don't do anything
		//System.out.println(RequestType[0]);
		if(RequestType[0].equals("GET")){
			//Spliting up the requests
			String[] Request = line.split(delims);
			String Content = Request[1].toLowerCase();
			String header = "";
			//Reading rest of lines to get headers
			while (line != null && !line.equals("")) {
				System.out.println(line);	
				line = reader.readLine();
				header = header.concat(line+"<br>");
			}
			OutputStreamWriter out = new OutputStreamWriter(clientConnection.getOutputStream());
			//Name request
			if(Content.equals("name")){
				out.write("<html><body>My name is Reggie Barnett<br>What I hope to get out of this class is a better "+
				"understanding of making applications for the web and to get better at programming</body></html>");
			}
			//Params request
			else if(Content.equals("params")){
				int Reqlen = Request.length;
				out.write("<html><body>");
				for(int i = 2; i <(Reqlen-2); i=i+2){
					out.write("<strong>"+Request[i]+"</strong>: "+Request[i+1]+"<br>");
				}
				out.write("</body></html>");
			}
			//Headers request
			else if(Content.equals("headers")){
				out.write("<html><body>"+header+"</body></html>");
			}
			//Any other request
			else{
				out.write("<html><body><h1>There's nothing here go away</h1></body></html>");
			}
			out.close();
		}
		//System.out.println("Finish Request\n");
	}
}