const container = document.getElementById('svgContainer')!

interface Land {
    name: string;
    group: SVGGElement;
    country?: "England" | "Germany" | "Russia" | "Turkey" | "AustroHungarian" | "Italy" | "France";
}

interface Water {
    name: string;
    group: SVGGElement;
}

interface Army {
    group: SVGGElement;
}

interface Flot {
    group: SVGGElement;
}


let land_bodies : Land[] = []
let water_bodies : Water[] = []
let armies : any[] = []
let fleets : any[] = []
let sources : any[] = []
let seen : any[] = []

let countries : {[key: string] : {landNames: string[], landObjects: Land[]}} = {
    England:  {
        landNames: ["Cly", "Edi", "Lvp", "Yor", "Wal", "Lon"],
        landObjects: []
    },
    Germany: {
        landNames: ["Kie", "Ruh", "Mun", "Ber", "Sil", "Pru"],
        landObjects: []
    },
    Russia: {
        landNames: ["Fin", "Stp", "Mos", "Lvn", "War", "Ukr", "Sev"],
        landObjects: []
    },
    Turkey: {
        landNames: ["Con", "Ank", "Smy", "Syr", "Arm"],
        landObjects: []
    },
    AustroHungarian: {
        landNames: ["Gal", "Vie", "Bud", "Tyr", "Boh", "Tri"],
        landObjects: []
    },
    Italy: { 
        landNames: ["Pie", "Ven", "Tus", "Rom", "Apu", "Nap"],
        landObjects: []
    },
    France: {
        landNames: ["Pic", "Bre", "Par", "Bur", "Gas", "Mar"],
        landObjects: []
    },
    Neutral: {
        landNames: ["Spa", "Por", "Bel", "Hol", "Den", "Nwy", "Swe", "Rum", "Bul", "Ser", "Gre", "Alb", "Naf", "Tun"],
        landObjects: [],
    },
    Unplayable: {
        landNames: [],
        landObjects: [],
    }
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
            // image.setAttribute("viewBox", "0 0 1000 1000");

            const image = container.querySelector("svg")!;
            const groups = image.querySelectorAll("g")!;

            discern_groups_populate_lists(groups);
            console.log(countries)
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
                    if (countries.Italy.landNames.includes(id)) {
                        console.log(id)
                        const path = element.querySelector("path").classList.add("italy")
                        land_bodies.push({group: element, name: id, country: "Italy"})
                        countries.Italy.landObjects.push({group: element, name: id, country: "Italy"})
                    }
                    else if (countries.France.landNames.includes(id)) {
                        const path = element.querySelector("path").classList.add("france")
                        land_bodies.push({group: element, name: id, country: "France"})
                        countries.Italy.landObjects.push({group: element, name: id, country: "France"})
                    }
                    else if (countries.Russia.landNames.includes(id)) {
                        const path = element.querySelector("path").classList.add("russia")
                        land_bodies.push({group: element, name: id, country: "Russia"})
                        countries.Italy.landObjects.push({group: element, name: id, country: "Russia"})
                    }
                    else if (countries.Turkey.landNames.includes(id)) {
                        const path = element.querySelector("path").classList.add("turkey")
                        land_bodies.push({group: element, name: id, country: "Turkey"})
                        countries.Italy.landObjects.push({group: element, name: id, country: "Turkey"})
                    }
                    else if (countries.England.landNames.includes(id)) {
                        const path = element.querySelector("path").classList.add("england")
                        land_bodies.push({group: element, name: id, country: "England"})
                        countries.Italy.landObjects.push({group: element, name: id, country: "England"})
                    }
                    else if (countries.AustroHungarian.landNames.includes(id)) {
                        const path = element.querySelector("path").classList.add("austrohungarian")
                        land_bodies.push({group: element, name: id, country: "AustroHungarian"})
                        countries.Italy.landObjects.push({group: element, name: id, country: "AustroHungarian"})
                    }
                    else if (countries.Germany.landNames.includes(id)) {
                        const path = element.querySelector("path").classList.add("germany")
                        land_bodies.push({group: element, name: id, country: "Germany"})
                        countries.Italy.landObjects.push({group: element, name: id, country: "Germany"})
                    }
                    else if (countries.Neutral.landNames.includes(id)) {
                        const path = element.querySelector("path").classList.add("neutral")
                        land_bodies.push({group: element, name: id})
                        countries.Italy.landObjects.push({group: element, name: id})
                    }
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


function colorPolygons() {
    // countries.England.landObjects.style.fill = "40597D";
}

function attachEvents() {
    land_bodies.forEach((element : Land) => {
        element.group.addEventListener("mouseover", (event) => {
            const divElement = document.getElementById("info") as HTMLDivElement
            let divText = "Land body: " + element.name;
            if (element.country) divText += ", Country: " + element.country;
            divElement.textContent = divText;
        })
    })

    water_bodies.forEach((element : Water) => {
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


