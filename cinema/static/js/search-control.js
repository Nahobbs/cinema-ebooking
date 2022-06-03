const open = document.getElementById ("modal_open")
const modal_container = document.getElementById ("modal_container")
const close = document.getElementById ("close")

open.oddEventListener('click',() =>{
    modal_container.classList.add('show');
} );

close.oddEventListener('click',() =>{
    modal_container.classList.remove('show');
} );
