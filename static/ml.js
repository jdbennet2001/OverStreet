let offset = 1

let issue = {};


// Clear existing data 
async function clear(){
    $('#cover').empty()
    $('#suggestions').empty()
}

async function renderIssue(basename, location){

    let cover = $('#cover')
    location = encodeURIComponent(location)
    location = encodeURIComponent(location)
    $('<img />', { src: `/cover/${location}`, class: 'cover-image' }).appendTo(cover)
    $('#title').html(basename)

}

async function renderSuggestions(issue, suggestions=[]){
    let pane = $('#suggestions')

    suggestions.forEach(suggestion => {
        renderSuggestion(pane, issue, suggestion)
    });


}

async function renderSuggestion(container, issue, suggestion){

    let {summary, pages, match, distance}  = suggestion;
    let {id, image, volume_name, issue_number, publisher, name, cover_date, volume_count_of_issues, url, description, month} = summary

    let card = $('<div>', { "class": 'suggestion', }).appendTo(container);

    let localImage = `/Volumes/LocalDASD/education/data/comic-vine/covers/${month}/${id}.jpg`
        localImage = encodeURIComponent(localImage)
        localImage = encodeURIComponent(localImage)

    let cover = $('<div>', { "class": 'cover', }).appendTo(card);

    let details = $('<div>', { "class": 'details' }).appendTo(card);
        
        $('<div>', { html: `<span class='column match-${match}'>Volume:</span> ${volume_name} (${distance})`, class: 'summary-line'}).appendTo(details);
        $('<div>', { html: `<span class='column'>Issue:</span> ${issue_number} of ${volume_count_of_issues}`, class: 'summary-line'}).appendTo(details);
        $('<div>', { html: `<span class='column'>Cover Date:</span> ${cover_date}`, class: 'summary-line'}).appendTo(details);
        $('<div>', { html: `<span class='column'>Title:</span> ${name}`, class: 'summary-line'}).appendTo(details);
        $('<div>', { html: `<span class='column'>Publisher:</span> ${publisher}`, class: 'summary-line'}).appendTo(details);
        $('<div>', { html: `<span class='column'>Pages:</span> ${pages}`, class: 'summary-line'}).appendTo(details);
        $('<div>', {html: `<span class='column'> <a href="${url}">Details</a> </span>`, class: 'summary-line'}).appendTo(details)
        

    // Stop rendering and just register a match if possible
    if ( issue.includes(issue_number)  && match && distance <= 0.55){
        await $.ajax('/classify', { data : JSON.stringify({issue, id}), contentType : 'application/json', type : 'POST' })
        render(++offset)
        return;
    }


    let img = $('<img />', { src: `/file/${localImage}`, class: 'cover-image' }).appendTo(cover)

        img.click(async () =>{
            await $.ajax('/classify', { data : JSON.stringify({issue, id}), contentType : 'application/json', type : 'POST' })
            render(++offset)
        })

}



async function render(index){


    let data = await fetch(`/comic/${index}`)
        .then((response) => { return response.json() })
        .catch((err) => { console.err(err)})

    let {basename, location, suggestions, remaining} = window.data = data

    await clear()

    if ( basename.includes('Chronology') )
        return render(++offset);

    await renderIssue(basename, location);

    await renderSuggestions(basename, suggestions)

    $('#count').text(remaining)

    console.log( data )

}

render(offset)

$('#next').click(() =>{
    render(++offset)
})

$('#skip').click(async () =>{
    let data = {issue: window.data['basename'], id: null}
    await $.ajax('/classify', { data : JSON.stringify(data), contentType : 'application/json', type : 'POST' })
    render(++offset)
})