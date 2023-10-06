const search_input = document.getElementById("real-time-search-input");
const results_box = document.getElementById("search-results-box");
const holder_div = document.getElementById("real-time-search-holder");
const chosen_films_box = document.getElementById("chosen-films-box");
const empty_state = document.getElementById("empty-state");
const chosen_films_input = document.getElementById("chosen-films-input");
const form = document.getElementById("list-form");
const reset_btn = document.getElementById("reset-btn");

const messages_holder = document.getElementById("messages-holder");

const csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value;

var added_film_ids = []

function sendSearchQuery(query) {
    $.ajax({
        type: "POST",
        url: "/searchFilms/",
        data: {
            csrfmiddlewaretoken: csrf,
            query: query,
        },
        success: (response) => {
            const data = response.data;

            if (Array.isArray(data)) {
                results_box.innerHTML = "";

                data.forEach((film) => {
                    results_box.innerHTML += `
                        <div class="real-time-search-result" data-id=${film.tmdb_id} data-title="${film.title}" data-year=${film.year} data-poster="${film.poster}">
                            <img class="poster-holder w70" src="https://image.tmdb.org/t/p/w154${film.poster}" alt="${film.title}">
                            <div class="flex-col" style="margin-left: 10px; z-index: 1;">
                                <span style="font-family: 'DM Serif Display', 'Serif'; font-size: 24px; line-height: 20px;">${film.title} <span style="font-family: 'Inter', 'Sans Serif'; margin-left: 3px; font-weight: 200; font-size: 12px;">${film.year}</span></span>
                                <span style="font-weight: 200; color: #b9b9b9; font-size: 12px;">Directed by ${film.directors}</span>
                            </div>
                        </div>
                    `;
                });

                const search_results = document.querySelectorAll(".real-time-search-result");

                search_results.forEach((result) => {
                    result.addEventListener("click", () => {
                        if (chosen_films_box.dataset.state == "empty") {
                            chosen_films_box.dataset.state = "not-empty";

                            chosen_films_box.style.border = "0";
                            chosen_films_box.style.minHeight = "fit-content";

                            empty_state.style.display = "none";
                        }

                        if (added_film_ids.includes(result.dataset.id)) {
                            messages_holder.innerHTML += `<div class="alerting-message alert">
                                                              <div class="alerting-message-body">
                                                                  You've already added ${result.dataset.title} (${result.dataset.year}) to your list.
                                                              </div>
                                                              <button onclick="closeMessage(this)" class="close-btn" style="position: static; margin: 0;">&times;</button>
                                                          </div>`;
                        } else {
                            chosen_films_box.innerHTML += `<li class="chosen-film-list-item" draggable="true" data-id=${result.dataset.id} data-title="${result.dataset.title}" data-year=${result.dataset.year} data-poster="${result.dataset.poster}">
                                                                <svg style="z-index: 1; flex-shrink: 0; flex-grow: 0;" width="0.75em" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 243 392"><circle fill="CurrentColor" cx="46" cy="46" r="40"/><circle fill="CurrentColor" cx="46" cy="196" r="40"/><circle fill="CurrentColor" cx="46" cy="346" r="40"/><circle fill="CurrentColor" cx="197" cy="46" r="40"/><circle fill="CurrentColor" cx="197" cy="196" r="40"/><circle fill="CurrentColor" cx="197" cy="346" r="40"/></svg>
                                                                <img class="poster-holder w70" style="margin: 0 15px; pointer-events: none;" src="https://image.tmdb.org/t/p/w154${result.dataset.poster}" alt="${result.dataset.title}">
                                                                <div class="flex-col">
                                                                    <span style="font-family: 'DM Serif Display', 'Serif'; font-size: 30px; line-height: 35px; z-index: 1;">${result.dataset.title} <span style="font-family: 'Inter', 'Sans Serif'; font-weight: 200; font-size: 15px;">${result.dataset.year}</span></span>
                                                                </div>
                                                                <span class="chosen-film-close-btn">
                                                                    <svg width="0.75em" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 102 102"><defs><style>.lfcb{fill:none;stroke-linecap:round;stroke-miterlimit:10;stroke-width:10px;}</style></defs><line stroke="CurrentColor" class="lfcb" x1="97" y1="5" x2="5" y2="97"/><line stroke="CurrentColor" class="lfcb" x1="5" y1="5" x2="97" y2="97"/></svg>
                                                                </span>
                                                            </li>`;

                           
                            added_film_ids.push(result.dataset.id);
                            
                            
                            var close_btns = document.querySelectorAll('.chosen-film-close-btn');

                            close_btns.forEach((btn)=> {
                                  btn.addEventListener('click', ()=> {
                                        let film_option = btn.parentElement;
                                        added_film_ids = added_film_ids.filter((id) => {
                                            return id !== film_option.dataset.id;
                                        });
                                        film_option.remove();

                                        if (added_film_ids.length == 0) {
                                          empty_state.style.display = 'block'; // Not Working, God knows why

                                          chosen_films_box.dataset.state = 'empty';
                                          chosen_films_box.removeAttribute('style');
                                        }
                                  })
                            })

                        }
                        

                    });
                });


            } else {
                results_box.innerHTML = `<div class="real-time-search-result">${data}</div>`;
            }
        },
        error: (err) => {
            console.log(err);
        },
    });
}



search_input.addEventListener("keyup", (e) => {
    if (results_box.classList.contains("invisible") && e.target.value != "") {
        results_box.classList.remove("invisible");
    } else if (e.target.value == "" && !results_box.classList.contains("invisible")) {
        results_box.classList.add("invisible");
    }

    if (e.target.value != "") {
        sendSearchQuery(e.target.value);
    }
});



const search_input_link = document.getElementById("search-input-link");

search_input_link.addEventListener("click", () => {
    search_input.focus();
});




document.addEventListener("click", (e) => {
    if (!holder_div.contains(e.target) && !search_input_link.contains(e.target)) {
        results_box.style.display = "none";
        search_input.style.outline = "1px #343446 solid";
        search_input.style.borderBottomLeftRadius = "0.375rem";
        search_input.style.borderBottomRightRadius = "0.375rem";
    } else {
        search_input.addEventListener("keyup", (x) => {
            if (x.target.value == "") {
                results_box.style.display = "none";
                search_input.style.outline = "2px #66f solid";
                search_input.style.borderBottomLeftRadius = "0.375rem";
                search_input.style.borderBottomRightRadius = "0.375rem";
            } else {
                results_box.style.display = "block";
                search_input.style.outline = "0";
                search_input.style.borderBottomLeftRadius = "0";
                search_input.style.borderBottomRightRadius = "0";
            }
        });
    }
});



form.addEventListener('submit', ()=> {

    var input = [];

    for (let i = 1; i < chosen_films_box.childElementCount; i++) {
        let child = chosen_films_box.children[i];
        input.push(child.dataset.id);
    }

    chosen_films_input.value = JSON.stringify(input);
});

reset_btn.addEventListener('click', ()=> {
    let i = 0;
    const count = chosen_films_box.childElementCount - 1;
    while(i < count) {
        chosen_films_box.children[1].remove();
        i++;
    }

    added_film_ids = [];
    empty_state.style.removeProperty('display');

    chosen_films_box.dataset.state = 'empty';
    chosen_films_box.removeAttribute('style');
})