<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
SOS School - Notice Archives & Cloud Audit Log
</title>

<style>

*{
    box-sizing:border-box
}

html,body{
    margin:0;
    width:100%;
    height:100%;
    font-family:"Segoe UI",Arial,sans-serif;
    background:#eaf5fc;
    color:#1a2a3a
}

body{
    overflow:hidden
}

.window{
    width:100%;
    height:100vh;
    padding:25px;
    display:flex;
    flex-direction:column;
    gap:15px
}

.header{
    min-height:34px;
    height:34px;
    display:flex;
    align-items:center
}

.back-button{
    height:34px;
    background:#e1f0fa;
    color:#0066b2;
    border-radius:6px;
    font-weight:bold;
    padding:0 12px;
    border:1px solid #b2d4ee;
    cursor:pointer
}

.back-button:hover{
    background:#cbe3f5
}

.title{
    margin-left:15px;
    color:#004080;
    font-size:16px;
    font-weight:700
}

.spacer{
    flex:1
}

.refresh{
    height:34px;
    background:#0077c8;
    color:#fff;
    border:0;
    border-radius:6px;
    padding:0 15px;
    font-weight:700;
    cursor:pointer
}

.card{
    flex:1;
    min-height:0;
    background:rgba(255,255,255,.95);
    border:1px solid #cbe3f5;
    border-radius:12px;
    padding:15px
}

.status{
    display:none;
    padding:8px 12px;
    margin-bottom:10px;
    border-radius:6px;
    font-size:11px;
    font-weight:700
}

.status.show{
    display:block
}

.table-wrap{
    width:100%;
    height:100%;
    overflow:auto;
    background:#fff;
    border:1px solid #b2d4ee;
    border-radius:8px
}

table{
    width:100%;
    min-width:900px;
    border-collapse:collapse;
    background:#fff
}

thead{
    background:#0077c8
}

th{
    background:#0077c8;
    color:#fff;
    padding:9px;
    text-align:center;
    position:sticky;
    top:0;
    z-index:2
}

td{
    background:#fff;
    padding:9px;
    border-top:1px solid #e1f0fa;
    vertical-align:top
}

tbody tr:hover td{
    background:#f5faff
}

.pdf-link{
    color:#0077c8;
    font-weight:700;
    text-decoration:none
}

.pdf-link:hover{
    text-decoration:underline
}

</style>

</head>

<body>

<main class="window">

<header class="header">

<button
    id="backButton"
    class="back-button"
>
⬅ Back to Admin Panel
</button>

<div class="title">
📚 Managed Notice Archive (Cloud Synced)
</div>

<div class="spacer"></div>

<button
    id="refreshButton"
    class="refresh"
>
🔄 Refresh Archives
</button>

</header>


<section class="card">

<div
    id="status"
    class="status"
></div>


<div class="table-wrap">

<table>

<thead>

<tr>

<th>
Target Group
</th>

<th>
Notice Title
</th>

<th>
Content Body
</th>

<th>
PDF Attachment
</th>

<th>
Timestamp
</th>

</tr>

</thead>


<tbody id="archiveBody"></tbody>

</table>

</div>

</section>

</main>


<script>

const DATA_ENDPOINT =
    "/api/admin/data";


const archiveBody =
    document.getElementById(
        "archiveBody"
    );


const status =
    document.getElementById(
        "status"
    );


const refreshButton =
    document.getElementById(
        "refreshButton"
    );


function escapeHTML(
    value
){

    return String(
        value ?? ""
    )
    .replace(
        /[&<>"']/g,
        character => ({
            "&":"&amp;",
            "<":"&lt;",
            ">":"&gt;",
            '"':"&quot;",
            "'":"&#39;"
        }[character])
    );
}


function fileName(
    url
){

    return String(
        url || ""
    )
    .replace(
        /\\/g,
        "/"
    )
    .split("/")
    .pop();
}


function formatDate(
    value
){

    if(!value){
        return "N/A";
    }


    const date =
        new Date(value);


    if(
        Number.isNaN(
            date.getTime()
        )
    ){

        return value;
    }


    return (
        date.toLocaleDateString(
            undefined,
            {
                month:"short",
                day:"2-digit",
                year:"numeric"
            }
        )
        +
        " - "
        +
        date.toLocaleTimeString(
            undefined,
            {
                hour:"2-digit",
                minute:"2-digit",
                hour12:true
            }
        )
    );
}


function showStatus(
    message,
    error=false
){

    status.textContent =
        message;


    status.classList.add(
        "show"
    );


    status.style.background =
        error
            ? "#fff0f0"
            : "#e1f0fa";


    status.style.border =
        "1px solid "+
        (
            error
                ? "#e2a5a5"
                : "#b2d4ee"
        );


    status.style.color =
        error
            ? "#9b2c2c"
            : "#004080";
}


async function loadArchive(){

    try{

        refreshButton.disabled =
            true;


        const response =
            await fetch(
                DATA_ENDPOINT,
                {
                    cache:"no-store"
                }
            );


        if(!response.ok){

            throw new Error(
                `Request failed: ${response.status}`
            );
        }


        const result =
            await response.json();


        const data =
            result.data || {};


        /*
         * IMPORTANT:
         * This is full history.
         * There is deliberately NO 12-hour filter.
         */
        const notices =
            Array.isArray(
                data.notices
            )
                ? data.notices
                : [];


        archiveBody.innerHTML =
            "";


        notices.forEach(
            notice => {

                const row =
                    document.createElement(
                        "tr"
                    );


                let pdfHTML =
                    "None";


                if(
                    typeof notice.pdf ===
                    "string"
                    &&
                    notice.pdf
                ){

                    const displayName =
                        notice.pdf_name ||
                        fileName(
                            notice.pdf
                        ) ||
                        "Open PDF";


                    pdfHTML =
                        `
                        <a
                            class="pdf-link"
                            href="${escapeHTML(notice.pdf)}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            ${escapeHTML(displayName)}
                        </a>
                        `;
                }


                row.innerHTML =
                    `
                    <td>
                        ${escapeHTML(
                            `${notice.target || "All"} (${notice.section || ""})`
                        )}
                    </td>

                    <td>
                        ${escapeHTML(
                            notice.title || ""
                        )}
                    </td>

                    <td>
                        ${escapeHTML(
                            notice.content ||
                            "No body text"
                        )}
                    </td>

                    <td>
                        ${pdfHTML}
                    </td>

                    <td>
                        ${escapeHTML(
                            formatDate(
                                notice.timestamp
                            )
                        )}
                    </td>
                    `;


                archiveBody.appendChild(
                    row
                );
            }
        );


        showStatus(
            `Loaded ${notices.length} notice record(s) from Supabase.`
        );


    }
    catch(error){

        showStatus(
            `Could not load notice history: ${error.message}`,
            true
        );

    }
    finally{

        refreshButton.disabled =
            false;
    }
}


refreshButton.onclick =
    loadArchive;


document.getElementById(
    "backButton"
).onclick =
    () => {

        window.location.href =
            "admin_panel.html";
    };


loadArchive();


setInterval(
    loadArchive,
    5000
);

</script>

</body>
</html>
