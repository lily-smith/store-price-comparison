import logo from './logo.svg';
import './App.css';
import { useEffect, useState } from 'react';

function App() {
  const [apiValue, setApiValue] = useState([]);

  useEffect(() => {
    fetch('/prices/1?search_term=eggs&zip_code=02155&city_name=Medford').then((res) => res.json()).then((data) => {
      setApiValue(data)
    })
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <p>API value:</p>
        { 
          apiValue.map((item) => (
              <div key={`${item.name},${item.price}`}>
                <p>{`${item.name} (${item.quantity})`}</p>
                <p>{item.price}</p>
                <p>{item.is_in_stock ? 'In Stock' : 'Out of Stock'}</p>
                <img src={item.image_url} width='150'/>
              </div>
            )
          ) 
        }
      </header>
    </div>
  );
}

export default App;
