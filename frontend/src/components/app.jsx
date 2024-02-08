import {useEffect, useState} from "preact/hooks";

const t = (t) => t * 1000;
const URL = "http://127.0.0.1:6969"

async function reqUpdate() {
    fetch(URL + "/update").then(async r => {
        console.log(await r.json());
    });
}

function PastGames({score}) {
    return (
        <div className={`${String(score).startsWith("-") ? "text-red-500" : "text-green-500"}`}>
            <p>{score}</p>
        </div>
    )
}

export function App() {
    const [pastGames, setPastGames] = useState([]);

    useEffect(() => {
        setInterval(() => {
            fetch(URL + "/update").then(async r => {
                // console.log(await r.json());
                setPastGames(await r.json())

            });
        }, t(2))
    }, []);

    return (
        <div>
            {pastGames.recent?.map((i) => {
                return <PastGames score={i} />
            })}
        </div>
    )
}
