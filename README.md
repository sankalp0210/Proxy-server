### team members
- pragun saxena(20171127)
- sankalp agarwal(20171161)

### Running the code
- go to system settings and set your http proxy on port 20100
- on terminal run command python proxy.py
- to add/change/delete usernames and password make changes to auth.txt
- to add/change/delete blocked websites , make changes to block.txt
- Now you can send request using curl or use firefox browser

### about the Server
- you won't be able to access blocked sites unless you login with credentials given in auth.txt
- the sever also maintains cache for frequently visited websites(stores websites data if not modified within 5 minutes)
- The server also uses threading for parallel processing 