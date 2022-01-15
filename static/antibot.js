function antiBot() {
    var answer;
    answer = document.getElementById("secquestion").value;
    if (answer != 40){
      alert("You must answer correctly security question!")
      return false;
    }
}
