/*switching signIn/signUp forms*/
const toggleBtns = document.querySelectorAll('.side .signin-btn');
const signIn = document.querySelector('.signin');
const signUp = document.querySelector('.signup');
const sides = document.querySelectorAll('.side');
const forms = document.querySelectorAll('.signin-form');

toggleBtns.forEach(btn => {btn.addEventListener('click',toggle)});

function toggle(){
   signIn.classList.toggle('hidden');
   signUp.classList.toggle('hidden');
   sides.forEach(side => {side.classList.toggle('left')});
   forms.forEach(form => {form.classList.toggle('right')});
}

/*Mobile Layout Animation*/
const mobileBtns = document.querySelectorAll('.btn.mobile-only');

mobileBtns.forEach(btn => {btn.addEventListener('click',mobileToggle)});

function mobileToggle(){
   signIn.classList.toggle('hidden');
   signUp.classList.toggle('hidden');
   signIn.classList.toggle('top');
}

/*SignUp form validation*/
const signUpForm = document.querySelector('.signup .signin-form');
const firstName = document.querySelector('#f-name');
const lastName = document.querySelector('#l-name');
const email = document.querySelector('#email');
const password = document.querySelector('#password');
const password2 = document.querySelector('#password2');
const phone = document.querySelector('#phone');

signUpForm.addEventListener('submit',checkValues);

function checkValues(e){
    const firstNameValue = firstName.value.trim();
    const lastNameValue = lastName.value.trim();
    const passwordValue = password.value.trim();
    const password2Value = password2.value.trim();
    const emailValue = email.value.trim();
    const phoneValue = phone.value.trim();
    // name validation
    if(firstNameValue === ""){
     showError(firstName,'Name cannot be empty');
     e.preventDefault();
    }
    else if(lastNameValue === ""){
        showError(lastName,'Name cannot be empty');
        e.preventDefault();
       }
    // email validation
    //checks if user exists
    if(email.getAttribute('id') == "doesnt-exist") {
        showError(email,'Existing user with this email');
        e.preventDefault();
    }
    else if(emailValue === ""){
        showError(email,'Email cannot be empty');
        e.preventDefault();
    }
    else if(emailValue.indexOf('@') === -1 || emailValue.indexOf(".") === -1){
        showError(email,'Please enter a valid email');
        e.preventDefault();
    }
    else{
        success(email);
    }
    // password validation
    if(passwordValue === ""){
        showError(password,'Password cannot be empty');
        e.preventDefault();
    }
    else if(passwordValue.length < 10){
        showError(password,'Password should be at least 10 characters');
        e.preventDefault();
    }
    else{
        success(password);
    }
    // retype password validation
    if(password2Value === ""){
     showError(password2,'Password cannot be empty');
     e.preventDefault();
     }
    else if(password2Value !== passwordValue){
        showError(password2,'Password does not match');
        e.preventDefault();
    }
    else{
        success(password2);
    }
    // phone validation
     if(phoneValue === ""){
     showError(phone,'Phone cannot be empty');
     e.preventDefault();
     }
    else if (phoneValue.length < 10){
        showError(phone, 'Phone invalid,')
        e.preventDefault();
    }
    else {
         success(phoneValue)
    }
 }

function showError(input,message){
   const formControl = input.parentElement;
   const error = formControl.querySelector('small');
   input.style.border = '2px solid red';
   error.innerText = message;
   error.style.visibility = 'visible';
}

function success(input){
   const formControl = input.parentElement;
   const error = formControl.querySelector('small');
   input.style.border = 'none';
   error.style.visibility = 'hidden';
}

/*Modal*/
const open = document.getElementById("modal_open")
const modalcontainer = document.getElementById("modalcontainer")
const close = document.getElementById("modal_close")

open.oddEventListener('click', () => {
    modalcontainer.classList.add('show');
});

close.oddEventListener('click', () => {
    modalcontainer.classList.remove('show');
});