const container = document.getElementById('svgContainer')!

interface land {
    name: string;
    group: SVGGElement;
    country?: "England" | "Germany" | "Russia" | "Turkey" | "AustroHungarian" | "Italy" | "France";
}

interface water {
    name: string;
    group: SVGGElement;
}

interface army {
    group: SVGGElement;
}

interface flot {
    group: SVGGElement;
}


let land_bodies : land[] = []
let water_bodies : water[] = []
let armies : any[] = []
let fleets : any[] = []
let sources : any[] = []
let seen : any[] = []

let countries = {
    England: ["Cly", "Edi", "Lvp", "Yor", "Wal", "Lon"],
    Germany: ["Kie", "Ruh", "Mun", "Ber", "Sil", "Pru"],
    Russia: ["Fin", "Stp", "Mos", "Lvn", "War", "Ukr", "Sev"],
    Turkey: ["Con", "Ank", "Smy", "Syr", "Arm"],
    AustroHungarian: ["Gal", "Vie", "Bud", "Tyr", "Boh", "Tri"],
    Italy: ["Pie", "Ven", "Tus", "Rom", "Apu", "Nap"],
    France: ["Pic", "Bre", "Par", "Bur", "Gas", "Mar"]
}

let mouse = {
    isDragging: false,
    draggingElement: null as SVGGElement | null,
    x_initial: 0,
    y_initial: 0,
    x_delta: 0,
    y_delta: 0,
    x_initial_translate: 0,
    y_initial_translate: 0,
}

// fetch("./static/diplomacy_wiki.svg")
fetch("/mapsvg")
    .then((response: Response) => response.text())
    .then((data: string) => {
        if (container) {
            container.innerHTML = data;
            const image = container.querySelector("svg")!;
            // image.setAttribute("viewBox", "0 0 1000 1000");

            const groups = image.querySelectorAll("g")!;

            discern_groups_populate_lists(groups);
            attachEvents();
        }
    }) .catch((error: Error) => {
        console.error('Error fetching SVG:', error);
    });


function discern_groups_populate_lists(groups) {
    groups.forEach((element) => {
        // console.log(element)
        // console.log(element.innerHTML)
        const textField = element.querySelector("text");
        // console.log(textField);
        // console.log(element.innerHTML)
        if (element.id == "F") {
            fleets.push(element)
            seen.push(element)
        }
        const internalGroup = element.querySelector("g")
        if (internalGroup) {
            if (internalGroup.id == "F") {
                fleets.push(internalGroup)
                seen.push(element)
            }
        }
        if (element.id == "A") {
            armies.push(element)
            seen.push(element)
        }
        if (internalGroup) {
            if (internalGroup.id == "A") {
                armies.push(internalGroup)
                seen.push(element)
            }
        }
        if (element.id == "sc") {
            sources.push(element)
            seen.push(element)
        }
        if (internalGroup) {
            if (internalGroup.id == "sc") {
                sources.push(internalGroup)
                seen.push(element)
            }
        }
        if (textField) {
            // console.log(element)
            // console.log(element.innerHTML)
            // console.log(textField.id)
            const id = textField.id
            if (id.length == 3) {
                if (id.toUpperCase() === id) {
                    water_bodies.push({group: element, name: id})
                } else {
                    if (countries.Italy.includes(id)) land_bodies.push({group: element, name: id, country: "Italy"}) 
                    else if (countries.France.includes(id)) land_bodies.push({group: element, name: id, country: "France"})
                    else if (countries.Russia.includes(id)) land_bodies.push({group: element, name: id, country: "Russia"})
                    else if (countries.Turkey.includes(id)) land_bodies.push({group: element, name: id, country: "Turkey"})
                    else if (countries.England.includes(id)) land_bodies.push({group: element, name: id, country: "England"})
                    else if (countries.AustroHungarian.includes(id)) land_bodies.push({group: element, name: id, country: "AustroHungarian"})
                    else land_bodies.push({group: element, name: id})
                }
                seen.push(element)
            }
        }
    })


    // let notseen : any[] = []
    // groups.forEach((element) => {
    //     if (! seen.includes(element)) {
    // console.log(element)
    // console.log(element.innerHTML)
    // // console.log(element.id)
    // // console.log(element.id == "F")
    //     }
    // })
    // console.log("not seen")
    // console.log(notseen)
    //
    // console.log("c a s w")
    // console.log(land_bodies)
    // console.log(armies)
    // console.log(sources)
    // console.log(water_bodies)
    // console.log("seen")
    // console.log(seen)
}


function attachEvents() {
    land_bodies.forEach((element : land) => {
        element.group.addEventListener("mouseover", (event) => {
            const divElement = document.getElementById("info") as HTMLDivElement
            let divText = "Land body: " + element.name;
            if (element.country) divText += ", Country: " + element.country;
            divElement.textContent = divText;
        })
    })

    water_bodies.forEach((element : water) => {
        element.group.addEventListener("mouseover", (event) => {
            const divElement = document.getElementById("info") as HTMLDivElement
            const divText = "Water body: " + element.name;
            divElement.textContent = divText;
        })
    })

    armies.concat(fleets).forEach((element : SVGGElement) => {
        element.addEventListener("mousedown", (event) => {
            mouse.isDragging = true;
            mouse.draggingElement = element;
            mouse.x_initial = event.clientX;
            mouse.y_initial = event.clientY;
            mouse.x_initial_translate = 0;
            mouse.y_initial_translate = 0;
            // console.log("initial: ", mouse.x_initial, mouse.y_initial)

            const currentTransform = element.getAttribute('transform');
            if (currentTransform) {
                let translation = currentTransform.slice(10, -1);
                const translation_xy = translation.split(", ").map(n => Number(n))

                if (translation_xy) {
                    mouse.x_initial_translate = translation_xy[0];
                    mouse.y_initial_translate = translation_xy[1];
                }
            }
        })
    })

    document.addEventListener('mousemove', (event) => {
        if (mouse.isDragging) {
            mouse.x_delta = event.clientX - mouse.x_initial;
            mouse.y_delta = event.clientY - mouse.y_initial;
            // console.log("current: ", event.clientX, event.clientY);
            // console.log("delta: ", mouse.x_delta, mouse.y_delta);
            
            mouse.draggingElement?.setAttribute('transform', `translate(${mouse.x_delta + mouse.x_initial_translate}, ${mouse.y_delta + mouse.y_initial_translate})`);
        }
    });

    document.addEventListener('mouseup', () => {
        mouse.isDragging = false;
        mouse.draggingElement = null;
    });
}


