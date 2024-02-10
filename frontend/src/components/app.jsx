import {useEffect, useState} from "preact/hooks";

const t = (t) => t * 1000;
const t_color = (i) => `${String(i).startsWith("-") ? "text-red-500" : "text-green-500"}`
const URL = "http://127.0.0.1:6969"

async function reqUpdate() {
    fetch(URL + "/update").then(async r => {
        console.log(await r.json());
    });
}

function PastGames({score, index}) {
    return (
        <div className={""}>
            <p className={`${t_color(score)} opacity-${100 - (index * 10)}`}>{score}</p>

        </div>
    )
}

export function App() {
    const [pastGames, setPastGames] = useState([]);

    useEffect(() => {
        setInterval(() => {
            fetch(URL + "/update").then(async r => {
                setPastGames(await r.json())
            });
        }, t(2))
    }, []);

    return (
        <div className={"text-2xl font-bold text-white"}>
            <p className={"text"}>
                FP: {pastGames.current ? pastGames.current : 0} / <span
                className={`${t_color(pastGames.all)}`}>{pastGames.all ? pastGames.all : 0} </span>in {pastGames.all_games_played ? pastGames.all_games_played : 0}
            </p>
            <div className={"flex flex-col text-lg text-right w-10"}>
                {pastGames.recent?.reverse().map((i, index) => {
                    return <PastGames score={i} index={index}/>
                })}
            </div>
        </div>
    )
}
