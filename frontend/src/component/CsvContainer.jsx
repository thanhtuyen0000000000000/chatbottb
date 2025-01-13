import  { useState } from 'react';
import PropTypes from 'prop-types';

function CsvContainer({ csvData, onFileUpload, rowsPerPage }) {
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = Math.ceil((csvData.length - 1) / rowsPerPage);

  const currentTableData = () => {
    const startIndex = (currentPage - 1) * rowsPerPage;
    return csvData.slice(startIndex + 1, startIndex + rowsPerPage + 1);
  };

  
  return (
    <div className="csv-container">
      <h3>Upload File CSV</h3>
      <input type="file" accept=".csv" onChange={onFileUpload} />
      {csvData.length > 0 && (
        <div className="csv-table-wrapper">
          <table className="csv-table">
            <thead>
              <tr>
                {csvData[0].map((header, index) => (
                  <th key={index}>{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {currentTableData().map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {row.map((cell, cellIndex) => (
                    <td key={cellIndex}>{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          <div className="pagination">
            {Array.from({ length: totalPages }, (_, i) => (
              <button
                key={i + 1}
                className={currentPage === i + 1 ? 'active' : ''}
                onClick={() => setCurrentPage(i + 1)}
              >
                {i + 1}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Thêm PropTypes cho các props:
CsvContainer.propTypes = {
    csvData: PropTypes.array.isRequired,        // Kiểm tra kiểu của csvData, phải là mảng
    onFileUpload: PropTypes.func.isRequired,    // Kiểm tra kiểu của onFileUpload, phải là hàm
    rowsPerPage: PropTypes.number.isRequired,   // Kiểm tra kiểu của rowsPerPage, phải là số
  };  

export default CsvContainer;
