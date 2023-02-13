$("#settings").submit(function () {
  const pc_name = $("#pc-name").text();
  const ip = $("#ip").text();
  const showtime = $("#show-speed").val();
  const play_news = $("#play").is(":checked").toString();
  const on = $("#on").is(":checked").toString();
  const from = $("#from").val();
  const to = $("#to").val();
  const from_a = $("#from-a").val();
  const to_a = $("#to-a").val();

  fetch(window.location.href, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      pc_name: pc_name,
      ip: ip,
      play_time: showtime,
      play_news: play_news,
      on: on,
      news_from: from,
      news_to: to,
      hours_from: from_a,
      hours_to: to_a,
    }),
  })
    .then((resp) => {
      if (resp.ok) show_success("Einstellungen erfolgreich übernommen");
    })
    .catch((err) => {
      show_error("Ein Fehler ist aufgetreten");
      console.log(err);
    });
  return false;
});
