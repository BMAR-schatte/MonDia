function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function show_success(message){
    const $el = $(`<span style='opacity:0' class='success msg'>${message}</span>`)
    $(".messages--container").prepend($el);
    await sleep(100)
    $el.css("opacity", "1");
    await sleep(5000)
    $el.css("opacity", "0");
    await sleep(300);
    $el.remove()
}

async function show_error(message){
    const $el = $(`<span style='opacity:0' class='error msg'>${message}</span>`)
    $(".messages--container").prepend($el);
    await sleep(100)
    $el.css("opacity", "1");
    await sleep(5000)
    $el.css("opacity", "0");
    await sleep(300);
    $el.remove()
}