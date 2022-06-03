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
   e.preventDefault();

   const firstNameValue = firstName.value.trim();
   const lastNameValue = lastName.value.trim();
   const passwordValue = password.value.trim();
   const password2Value = password2.value.trim();
   const emailValue = email.value.trim();
   const phoneValue = phone.value.trim();

   if(emailValue === ""){
       showError(email,'Email cannot be empty');
   }
   else if(emailValue.indexOf('@') === -1 || emailValue.indexOf(".") === -1){
       showError(email,'Please enter a valid email');
   }
   else{
       success(email);
   }

   if(passwordValue === ""){
       showError(password,'Password cannot be empty');
   }
   else if(passwordValue.length < 10){
       showError(password,'Password should be at least 10 characters');
   }
   else{
       success(password);
   }

   if(password2Value !== passwordValue){
       showError(password2,'Password does not match');
   }
   else{
       success(password2);
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
