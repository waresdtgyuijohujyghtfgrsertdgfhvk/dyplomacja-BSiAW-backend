import {v4 as uuid} from "uuid";

const container = document.getElementById('svgContainer')!


type CountryName = "england" | "germany" | "russia" | "turkey" | "austrohungarian" | "italy" | "france" | "neutral";

interface Land {
    name: string;
    group: SVGGElement;
    country?: CountryName;
}

interface Water {
    name: string;
    group: SVGGElement;
}

interface Army {
    group: SVGGElement;
    uuid: string;
}

interface Fleet {
    group: SVGGElement;
    uuid: string;
}

interface Source {
    group: SVGGElement;
    uuid: string;
    country?: CountryName;
}



let myCountry : CountryName;
let land_bodies : Land[] = [];
let water_bodies : Water[] = [];
let armies : Army[] = [];
let fleets : Fleet[] = [];
let sources : Source[] = [];
let seen : any[] = [];
let arrowBundles: { arrow: Arrow, figure: SVGGElement, uuid: string}[] = []

class Arrow {
    start: number[];
    end: number[];
    x: number;
    y: number;
    arrowGroup: SVGGElement;
    triangle: SVGPolygonElement;
    line: SVGLineElement;
    circles: SVGCircleElement[];
    uuid: string;

    constructor(uuid: string, start: number[], end?: number[]) {
        this.uuid = uuid;
        const svgNamespace = "http://www.w3.org/2000/svg";
        const image = container.querySelector("svg")!;
        const rect = image.getBoundingClientRect();
        this.arrowGroup = document.createElementNS(svgNamespace, "g");
        this.triangle = document.createElementNS(svgNamespace, "polygon");
        this.line = document.createElementNS(svgNamespace, "line");

        this.setInitialCoordinates(start, end);
        
        const triangleCoordinates = [this.end, [this.end[0] - 20, this.end[1] - 12], [this.end[0] + 20, this.end[1] - 12]]
        let trianglePointsProperty = "";
        for (let i = 0; i < triangleCoordinates.length; i++) {
            trianglePointsProperty += String(triangleCoordinates[i][0]) + "," + String(triangleCoordinates[i][1]) + " "
        }

        trianglePointsProperty = trianglePointsProperty.trimEnd()

        this.triangle.setAttribute("points", trianglePointsProperty);
        this.triangle.setAttribute("pointer-events", "none");
        this.line.setAttribute("style", "stroke:red;stroke-width:2")
        this.line.setAttribute("pointer-events", "none");
        this.arrowGroup.appendChild(this.triangle);
        this.arrowGroup.appendChild(this.line);
        this.circles = [];
        image.appendChild(this.arrowGroup);
        // console.log(this)
    }

    update(end?: number[]) {
        if (end) this.updateCoordinates(end)
        const distance = Math.sqrt(this.x**2 + this.y**2);
        let angle = this.findAngle() + Math.PI / 2;
        const matrix = transformMatrix(this.x, this.y, angle);
        // let transformProperty = `transform: rotate(${angle}rad, ${this.start[0]}, ${this.start[1]}) translate(${this.x}, ${this.y})`
        // let transformProperty = `transform: rotate(${angle}rad, ${this.start[0]}, ${this.start[1]})`
        
        let triangleCoordinates = this.end
        let clockwise = -Math.PI / 8
        let antiClockwise = - clockwise 
        const arrowSide = 8
        this.triangle.setAttribute("transform", "");

        this.line.setAttribute("x1", String(this.start[0]));
        this.line.setAttribute("y1", String(this.start[1]));
        this.line.setAttribute("x2", String(this.end[0]));
        this.line.setAttribute("y2", String(this.end[1]));
        // console.log("this arrow element", this.arrowGroup)
        // console.log(this)
    }

    setInitialCoordinates(start: number[], end?: number[]) {
        const image = container.querySelector("svg")!;
        const rect = image.getBoundingClientRect();
            this.start = [start[0] - rect.left, start[1] - rect.top];
            if (end){
                this.end = [end[0] - rect.left, end[1] - rect.top];
            } else {
                this.end = this.start;
            }
            this.x = this.end[0] - this.start[0];
            this.y = this.end[1] - this.start[1];
    }

    updateCoordinates(end: number[]) {
        const image = container.querySelector("svg")!;
        const rect = image.getBoundingClientRect();
        this.end = [end[0] - rect.left, end[1] - rect.top];
        this.x = this.end[0] - this.start[0];
        this.y = this.end[1] - this.start[1];
    }

    findAngle() {
        let angle: number;
        if (this.x) {
            angle = Math.atan(this.y / this.x);
            if (this.x < 0) angle += Math.PI;
        } else {
            angle = 0;
        }
        return angle;
    }

    rotateVector(vector: number[], angle: number) {
        const x = vector[0]
        const y = vector[1]
        const rotated = [Math.cos(angle) * x + Math.sin(angle) * x, ]
    }
}


function transformMatrix(x: number, y: number, angle: number, x_extend?: number, y_extend?: number) {
    let matrix = `${Math.cos(angle)}, ${Math.sin(angle)}, ${-Math.sin(angle)}, ${Math.cos(angle)}, ${x}, ${y}`
    matrix = "matrix(" + matrix + ")";
    return matrix
}



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
    arrow: null as Arrow | null,
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
            attachEvents();
        }
    }) .catch((error: Error) => {
        console.error('Error fetching SVG:', error);
    });


function discern_groups_populate_lists(groups) {
    groups.forEach((element) => {
        const textField = element.querySelector("text");
        let country: CountryName = "neutral";
        let countryList = ["england" , "germany" , "russia" , "turkey" , "austrohungarian" , "italy" , "france"];
        countryList.forEach((countryChoise) => {
            if (element.querySelector("path").classList.contains(countryChoise)) {
                country = countryChoise as CountryName;
            } 
        })
        
        if (element.id == "F") {
            fleets.push({group: element, uuid: uuid()})
            element.classList.add("fleet")
            element.classList.add(country)
            seen.push(element)
        }
        if (element.id == "A") {
            armies.push({group: element, uuid: uuid()})
            element.classList.add("army")
            element.classList.add(country)
            seen.push(element)
        }
        if (element.id == "sc") {
            sources.push({group: element, uuid: uuid(), country: country})
            element.classList.add("source")
            element.classList.add(country)
            seen.push(element)
        }
        if (textField) {
            const id = textField.id
            if (id.length == 3) {
                if (id.toUpperCase() === id) {
                    water_bodies.push({group: element, name: id})
                } else {
                    if (countries.Italy.landNames.includes(id)) {
                        const path = element.querySelector("path").classList.add("italy")
                        land_bodies.push({group: element, name: id, country: "italy"})
                        countries.Italy.landObjects.push({group: element, name: id, country: "italy"})
                    }
                    else if (countries.France.landNames.includes(id)) {
                        const path = element.querySelector("path").classList.add("france")
                        land_bodies.push({group: element, name: id, country: "france"})
                        countries.Italy.landObjects.push({group: element, name: id, country: "france"})
                    }
                    else if (countries.Russia.landNames.includes(id)) {
                        const path = element.querySelector("path").classList.add("russia")
                        land_bodies.push({group: element, name: id, country: "russia"})
                        countries.Italy.landObjects.push({group: element, name: id, country: "russia"})
                    }
                    else if (countries.Turkey.landNames.includes(id)) {
                        const path = element.querySelector("path").classList.add("turkey")
                        land_bodies.push({group: element, name: id, country: "turkey"})
                        countries.Italy.landObjects.push({group: element, name: id, country: "turkey"})
                    }
                    else if (countries.England.landNames.includes(id)) {
                        const path = element.querySelector("path").classList.add("england")
                        land_bodies.push({group: element, name: id, country: "england"})
                        countries.Italy.landObjects.push({group: element, name: id, country: "england"})
                    }
                    else if (countries.AustroHungarian.landNames.includes(id)) {
                        const path = element.querySelector("path").classList.add("austrohungarian")
                        land_bodies.push({group: element, name: id, country: "austrohungarian"})
                        countries.Italy.landObjects.push({group: element, name: id, country: "austrohungarian"})
                    }
                    else if (countries.Germany.landNames.includes(id)) {
                        const path = element.querySelector("path").classList.add("germany")
                        land_bodies.push({group: element, name: id, country: "germany"})
                        countries.Italy.landObjects.push({group: element, name: id, country: "germany"})
                    }
                    else if (countries.Neutral.landNames.includes(id)) {
                        const path = element.querySelector("path").classList.add("neutral")
                        land_bodies.push({group: element, name: id})
                        countries.Italy.landObjects.push({group: element, name: id, country: "neutral"})
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
    // console.log("l a s w")
    // console.log(land_bodies)
    // console.log(armies)
    // console.log(sources)
    // console.log(water_bodies)
    // console.log("seen")
    // console.log(seen)
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

    armies.concat(fleets).forEach((object : Army | Fleet) => {
        const element = object.group;
        const bbox = element.getBBox();
        const centroid = [bbox.x + (bbox.width / 2), bbox.y + (bbox.height / 2)];
        element.addEventListener("mousedown", (event) => {
            mouse.isDragging = true;
            mouse.draggingElement = element;
            mouse.x_initial = event.clientX;
            mouse.y_initial = event.clientY;
            mouse.x_initial_translate = 0;
            mouse.y_initial_translate = 0;

            // const uuid = object.uuid;
            // const arrowBundle = arrowBundles.find(arrowBundle => arrowBundle.uuid === uuid);
            // if (arrowBundle) {
            //     mouse.arrow = arrowBundle.arrow;
            // } else {
            //     const newArrow = new Arrow(uuid, [mouse.x_initial, mouse.y_initial]);
            //     // console.log("arrow bundles 3", ...arrowBundles)
            //     arrowBundles.push({arrow: newArrow, figure: element, uuid: uuid});
            //     // console.log("arrow bundles 4", ...arrowBundles)
            //     mouse.arrow = newArrow;
            // }
            // console.log("arrow bundles", ...arrowBundles)

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
            
            const drag = mouse.draggingElement!;
            const arrow = mouse.arrow!;
            drag.setAttribute('transform', `translate(${mouse.x_delta + mouse.x_initial_translate}, ${mouse.y_delta + mouse.y_initial_translate})`);
            // const arrowBundle = arrowBundles.find(arrowBundle => arrowBundle.uuid === arrow.uuid);
            const pos = [event.clientX, event.clientY];
            // console.log("pos", pos)
            // arrowBundle?.arrow.update(pos);
        }
    });

    document.addEventListener('mouseup', () => {
        mouse.isDragging = false;
        mouse.draggingElement = null;
        mouse.arrow = null;
    });
}


