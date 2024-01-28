document.addEventListener("DOMContentLoaded", function () {
    fetch("http://software.diu.edu.bd:8006/result/semesterList")
        .then(response => response.json())
        .then(data => {
            const semesterSelect = document.getElementById("semester");
            data.forEach(semester => {
                const option = document.createElement("option");
                option.value = semester.semesterId;
                option.text = `${semester.semesterName} ${semester.semesterYear}`;
                semesterSelect.appendChild(option);
            });
        })
        .catch(error => console.error("Error fetching semester data:", error));

    document.getElementById("submitButton").addEventListener("click", function () {
        const inputText = document.getElementById("id").value;
        fetch(`http://software.diu.edu.bd:8006/result/studentInfo?studentId=${inputText}`)
            .then(response => response.json())
            .then(studentInfo => {
                const stInfoDiv = document.querySelector(".stinfo");
                stInfoDiv.innerHTML = `
                <div class="info-container">
                    <h2 style="text-align: center; color: #009933; ">Student Information</h2>
                    <p>Name: ${studentInfo.studentName}</p>
                    <p>Program: ${studentInfo.progShortName}</p>
                    <p>Batch No: ${studentInfo.batchNo}</p>
                </div>
            `;

                const selectedSem = document.getElementById("semester").value;
                fetch(`http://software.diu.edu.bd:8006/result?grecaptcha=&semesterId=${selectedSem}&studentId=${inputText}`)
                    .then(response => response.json())
                    .then(resultData => {
                        const resultTableDiv = document.querySelector(".resultTable");
                        resultTableDiv.innerHTML = `
                        <h2 style="text-align: center; color: #009933;">Result</h2>
                        <table class="stresult"></table>
                        `;
                        const resultTable = document.querySelector(".stresult");

                        const headerRow = resultTable.insertRow(0);
                        const headerMappings = {
                            customCourseId: "Course Code",
                            courseTitle: "Course Name",
                            totalCredit: "Credit",
                            gradeLetter: "GPA",
                            pointEquivalent: "CGPA"
                        };

                        Object.keys(headerMappings).forEach(key => {
                            const th = document.createElement("th");
                            th.textContent = headerMappings[key];
                            headerRow.appendChild(th);
                        });

                        const columnMappings = {
                            customCourseId: "Course Code",
                            courseTitle: "Course Name",
                            totalCredit: "Credit",
                            gradeLetter: "GPA",
                            pointEquivalent: "CGPA"
                        };

                        resultData.forEach(rowData => {
                            const row = resultTable.insertRow();
                            Object.keys(columnMappings).forEach(key => {
                                const cell = row.insertCell();
                                cell.textContent = rowData[key];
                            });
                        });

                        const totalCgpaRow = resultTable.insertRow();
                        const totalCgpaCell = totalCgpaRow.insertCell();
                        totalCgpaCell.colSpan = Object.keys(columnMappings).length - 1;
                        totalCgpaCell.textContent = "Total CGPA";
                        const cgpaCell = totalCgpaRow.insertCell();
                        cgpaCell.textContent = (resultData.reduce((sum, rowData) => sum + rowData["cgpa"], 0) / resultData.length).toFixed(2);

                        const downloadButton = document.getElementById("downloadButton");
                        downloadButton.style.display = "block";

                        downloadButton.addEventListener("click", function () {
                            fetch("/generate_pdf", {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json"
                                },
                                body: JSON.stringify({ data: resultData, stdData: studentInfo })
                            })
                                .then(response => response.json())
                                .then(data => {
                                    const pdfContent = data.pdf_content;
                                    const blob = new Blob([pdfContent], { type: 'application/pdf' });
                                    const link = document.createElement('a');
                                    link.href = window.URL.createObjectURL(blob);
                                    link.download = studentInfo.studentId+".pdf";
                                    link.click();
                                })
                                .catch(error => console.error("Error generating PDF:", error));
                        });
                    })
                    .catch(error => console.error("Error fetching result data:", error));
            })
            .catch(error => console.error("Error fetching student info:", error));
    });
});
