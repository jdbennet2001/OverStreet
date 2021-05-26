// Load list of comics that need


let key = undefined;


async function tag(){

    let data = { key, 'state': 'match'}
    await $.ajax('/classify', { data : JSON.stringify(data), contentType : 'application/json', type : 'POST' })
    next()    
}

async function skip(){
    let data = { key, 'state': 'skip'}
    await $.ajax('/classify', { data : JSON.stringify(data), contentType : 'application/json', type : 'POST' })
    next() }

async function next(){

    // Clear existing data
    $('#left').empty()
    $('#right').empty()

    // Double encode data to get around Python Flask issues
    key = keys.pop()

   

    let data = await fetch(`/comic/${encodeURIComponent(encodeURIComponent(key))}`)
    .then((response) => { return response.json() })
    .catch((err) => { console.log(err)})

    let {comic, location, page_count, match} = data;

    await renderIssue(comic, location, page_count)
    await renderSuggestion( match )

    $('#count').text(`(${keys.length})`)

    console.log(data)
}

async function renderIssue(basename, location, page_count){

    let path_to_comic = location.replace('Storage', 'LocalDASD')
    let image = `/cover/${encodeURIComponent(encodeURIComponent(path_to_comic))}`

    let trade_class = page_count >= 100 ? 'trade' : 'single'
    
    let left_pane = $('#left')
    let cover = $('<div>', {class: 'cover'}).appendTo(left_pane)
                $('<img />', { src: image, class: 'cover-image' }).appendTo(cover)
    
    $('<div>', { class: `title ${trade_class}`, html: basename}).appendTo(left_pane)
    $('<div>', { class: 'title', text: `${page_count} pages`}).appendTo(left_pane)  

}

async function renderSuggestion(match){

    let {cover_date, description, publisher, id, month, url, issue_number, volume_count_of_issues, volume_name, name} = match
    
    let image = `/Volumes/LocalDASD/education/data/comic-vine/covers/${month}/${id}.jpg`
        image = encodeURIComponent(image)
        image = encodeURIComponent(image)

    let publisher_class = (publisher == 'DC Comics' || publisher == 'Marvel') ? 'pub-main' : 'pub-other'
    let trade_class = (issue_number == 1 && volume_count_of_issues == 1) ? 'trade' : 'single'

    let right_pane = $('#right')
    let cover = $('<div>', {class: 'cover'}).appendTo(right_pane)
                $('<img />', { src: `/file/${image}`, class: `cover-image ${publisher_class}` }).appendTo(cover)

    let details = $('<div>', { "class": 'details' }).appendTo(right_pane);

        
        $('<div>', { html: `<span class='column match-${match}'>Volume:</span> ${volume_name}`, class: `summary-line ${trade_class}`}).appendTo(details);
        $('<div>', { html: `<span class='column'>Issue:</span> ${issue_number} of ${volume_count_of_issues}`, class: 'summary-line'}).appendTo(details);
        $('<div>', { html: `<span class='column'>Cover Date:</span> ${cover_date}`, class: 'summary-line'}).appendTo(details);
        $('<div>', { html: `<span class='column'>Title:</span> ${name}`, class: 'summary-line'}).appendTo(details);
        $('<div>', { html: `<span class='column'>Publisher:</span> ${publisher}`, class: 'summary-line'}).appendTo(details);
        $('<div>', {html: `<span class='column'> Details: <a href="${url}">${id}</a> </span>`, class: 'summary-line'}).appendTo(details)
       
        $('<div>', {html: description, class: 'summary-line'}).appendTo(details)
}

async function init(){

    let data = await fetch(`/comics`).then((response) => { return response.json() })

    keys = data.keys;

    //Set up action handlers
    $('#skip').click(() =>{ skip() })
    $('#tag').click(() =>{ tag() })

    $( "#body" ).keypress(function(a) {
        if (a.keyCode == 115) skip();
        else if (a.keyCode == 116) tag()
      });

    next()

    console.log( data )
}

init()