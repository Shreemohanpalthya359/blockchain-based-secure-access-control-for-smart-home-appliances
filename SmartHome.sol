pragma solidity >= 0.8.11 <= 0.8.11;
pragma experimental ABIEncoderV2;
//SmartHome solidity code
contract SmartHome {

    uint public commandCount = 0; 
    mapping(uint => command) public commandList; 
     struct command
     {
       string user_id;
       string sensor;
       string command_value;
       string command_date;       
     }
 
   // events 
   event commandCreated(uint indexed _commandId);

  
   //function  to save command details
   function createCommand(string memory uid, string memory sen,string memory cv, string memory cd) public {
      commandList[commandCount] = command(uid, sen, cv, cd);
      emit commandCreated(commandCount);
      commandCount++;
    }

     //get command count
    function getCommandCount()  public view returns (uint) {
          return commandCount;
    }    

    function getUserid(uint i) public view returns (string memory) {
        command memory s = commandList[i];
	return s.user_id;
    }

    function getSensor(uint i) public view returns (string memory) {
        command memory s = commandList[i];
	return s.sensor;
    }

    function getCommandValue(uint i) public view returns (string memory) {
        command memory s =commandList[i];
	return s.command_value;
    }

    function getCommandDate(uint i) public view returns (string memory) {
        command memory s =commandList[i];
	return s.command_date;
    }

    uint public userCount = 0; 
    mapping(uint => user) public userList; 
     struct user
     {
       string username;
       string password;
       string phone;      
       string email;
       string home_address;
     }
 
   // events
 
   event userCreated(uint indexed _userId);
 
  function createUser(string memory _username, string memory _password, string memory _phone, string memory email, string memory ha) public {
      userList[userCount] = user(_username, _password, _phone, email, ha);
      emit userCreated(userCount);
      userCount++;
    }

    //get user count
    function getUserCount()  public view returns (uint) {
          return  userCount;
    }

    function getUsername(uint i) public view returns (string memory) {
        user memory usr = userList[i];
	return usr.username;
    }

    function getPassword(uint i) public view returns (string memory) {
        user memory usr = userList[i];
	return usr.password;
    }

    function getEmail(uint i) public view returns (string memory) {
        user memory usr = userList[i];
	return usr.email;
    }   

    function getAddress(uint i) public view returns (string memory) {
        user memory usr = userList[i];
	return usr.home_address;
    }   

    
    function getPhone(uint i) public view returns (string memory) {
        user memory usr = userList[i];
	return usr.phone;
    }   
            
}