/*
~ paste into html for jquery functions:
~ <script src="https://code.jquery.com/jquery-3.6.0.js"></script>
*/

/* -------------------------------------------------------------------------- */
//*                               hover functions                             */
/* -------------------------------------------------------------------------- */

//* all <a> tags
$("a").hover(
    function () {
    $(this).addClass("mouseover-text");
    },
    function () {
    $(this).removeClass("mouseover-text");
});
//* button class 
$(".button").hover(function (){
    $(this).addClass("mouseover-button");
    },
    function () {
    $(this).removeClass("mouseover-button");
});
//* anchors that are styled like buttons
$(".button-anchor").hover(function (){
    $(this).addClass("mouseover-button-anchor");
    },
    function () {
    $(this).removeClass("mouseover-button-anchor");
});
