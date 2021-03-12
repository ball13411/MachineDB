// Greeting
var myDate = new Date();
var hrs = myDate.getHours();

var greet;

if (hrs < 12)
    greet = 'Good Morning';
else if (hrs >= 12 && hrs <= 17)
    greet = 'Good Afternoon';
else if (hrs >= 17 && hrs <= 24)
    greet = 'Good Evening';

document.getElementById('Greetings').innerHTML = '<b>' + greet + '</b>';

// Date
const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    let current_datetime = new Date()
    let formatted_date = current_datetime.getDate() + " " + months[current_datetime.getMonth()] + " " + current_datetime.getFullYear()
    document.getElementById('today-date').innerHTML = formatted_date
