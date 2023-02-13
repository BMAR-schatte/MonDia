async function set_error(selector, description="* Error") {
    const elm = $(selector);
    if (elm.next().attr("id") != `${elm.attr("id")}-e`){
    elm.addClass("input-red");
    elm.after(function(){
        return `<span class='input-error' id='${elm.attr("id")}-e'>${description}</span>`
    })
}
}