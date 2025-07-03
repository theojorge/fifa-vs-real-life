import React, { useState } from "react";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000"; // Fallback para desarrollo local

export default function App() {
  const [playerName, setPlayerName] = useState("");
  const [loading, setLoading] = useState(false);
  const [cards, setCards] = useState([]);
  const [error, setError] = useState(null);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'ascending' });

  const fetchPlayerData = async () => {
    setLoading(true);
    setError(null);
    setCards([]);

    try {
      const res = await fetch(`${API_BASE_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ player_name: playerName }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || "Error desconocido");
      }

      const data = await res.json();
      setCards(data);
    } catch (err) {
      setError(err.message);
    }

    setLoading(false);
  };

  const formatValue = (val) => {
    if (val != null && val !== "") {
        const str = val.toString();
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
    return "N/A";
   };

  const formatCurrency = (val) =>
    val != null && !isNaN(val) ? `€${Math.round(val).toLocaleString()}` : "N/A";

  const getCardTypeColor = (cardType) => {
    const cardStr = cardType?.toString().toLowerCase() || '';
    
    if (cardStr.includes('totw')) return 'linear-gradient(135deg, #FFD700, #FFA500)';
    if (cardStr.includes('toty')) return 'linear-gradient(135deg, #1E90FF, #00BFFF)';
    if (cardStr.includes('tots')) return 'linear-gradient(135deg, #1E90FF, #00BFFF)';
    if (cardStr.includes('icon')) return 'linear-gradient(135deg, #FF1493, #FF69B4)';
    if (cardStr.includes('hero')) return 'linear-gradient(135deg, #32CD32, #90EE90)';
    if (cardStr.includes('special')) return 'linear-gradient(135deg, #9370DB, #DDA0DD)';
    if (cardStr.includes('rare')) return 'linear-gradient(135deg, #FFD700, #FFFF00)';
    if (cardStr.includes('ormal')) return 'linear-gradient(135deg, #FFD700, #FFFF00)';
    if (cardStr.includes('if')) return 'linear-gradient(135deg, #FFD700, #FFA500)';
    return 'linear-gradient(135deg, #4CAF50, #81C784)'; // default
  };

  const getRatingColor = (rating) => {
    if (rating >= 90) return '#FFD700';
    if (rating >= 85) return '#FF6B35';
    if (rating >= 80) return '#4ECDC4';
    if (rating >= 75) return '#45B7D1';
    return '#96CEB4';
  };

  const sortData = (key) => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  const parsePriceValue = (priceStr) => {
    if (typeof priceStr !== 'string') {
      return parseFloat(priceStr) || 0;
    }

    let value = priceStr.toLowerCase().replace(/[^0-9.]/g, ''); 
    if (priceStr.toLowerCase().includes('k')) {
      return parseFloat(value) * 1000; 
    }
    if (priceStr.toLowerCase().includes('m')) {
      return parseFloat(value) * 1000000; 
    }
    return parseFloat(value); 
  };

  const getSortedCards = () => {
    let sortableCards = [...cards]; 
    if (sortConfig.key) {
      sortableCards.sort((a, b) => {
        let aValue = a[sortConfig.key];
        let bValue = b[sortConfig.key];

        if (aValue == null || aValue === "") aValue = "";
        if (bValue == null || bValue === "") bValue = "";

        if (sortConfig.key === 'price') {
          aValue = parsePriceValue(a[sortConfig.key]);
          bValue = parsePriceValue(b[sortConfig.key]);
        } else {
          const aNum = parseFloat(aValue);
          const bNum = parseFloat(bValue);
          
          if (!isNaN(aNum) && !isNaN(bNum)) {
            aValue = aNum; 
            bValue = bNum;
          } else {
            aValue = aValue.toString().toLowerCase();
            bValue = bValue.toString().toLowerCase();
          }
        }

       
        if (aValue < bValue) {
          return sortConfig.direction === 'ascending' ? -1 : 1;
        }
        if (aValue > bValue) {
          return sortConfig.direction === 'ascending' ? 1 : -1;
        }
        return 0; 
      });
    }
    return sortableCards; 
  };

  const getSortIcon = (columnKey) => {
    if (sortConfig.key === columnKey) {
      return sortConfig.direction === 'ascending' ? ' ▲' : ' ▼';
    }
    return '';
  };

  const sortedCards = getSortedCards();

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '40px 20px',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        background: 'rgba(255, 255, 255, 0.95)',
        borderRadius: '20px',
        padding: '40px',
        boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
        backdropFilter: 'blur(10px)'
      }}>
        <h1 style={{
          textAlign: 'center',
          fontSize: '2.5rem',
          background: 'linear-gradient(135deg, #667eea, #764ba2)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          marginBottom: '30px',
          fontWeight: 'bold',
          textShadow: '2px 2px 4px rgba(0,0,0,0.1)'
        }}>
          ⚽ Valor de carta de FIFA Ultimate Team en la vida real ⚽
        </h1>

        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '15px',
          marginBottom: '30px',
          flexWrap: 'wrap'
        }}>
          <input
            type="text"
            placeholder="🔍 Ingrese nombre del jugador"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            style={{
              padding: '15px 20px',
              fontSize: '16px',
              border: '3px solid transparent',
              borderRadius: '15px',
              background: 'linear-gradient(white, white) padding-box, linear-gradient(135deg, #667eea, #764ba2) border-box',
              outline: 'none',
              minWidth: '300px',
              transition: 'all 0.3s ease',
              boxShadow: '0 5px 15px rgba(0,0,0,0.1)'
            }}
            onFocus={(e) => {
              e.target.style.transform = 'scale(1.02)';
              e.target.style.boxShadow = '0 8px 25px rgba(102, 126, 234, 0.3)';
            }}
            onBlur={(e) => {
              e.target.style.transform = 'scale(1)';
              e.target.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
            }}
          />

          <button
            onClick={fetchPlayerData}
            disabled={loading || !playerName}
            style={{
              padding: '15px 30px',
              fontSize: '16px',
              fontWeight: 'bold',
              border: 'none',
              borderRadius: '15px',
              background: loading || !playerName 
                ? 'linear-gradient(135deg, #ccc, #999)' 
                : 'linear-gradient(135deg, #FF6B35, #FF8E53)',
              color: 'white',
              cursor: loading || !playerName ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: '0 5px 15px rgba(0,0,0,0.2)',
              minWidth: '120px'
            }}
            onMouseEnter={(e) => {
              if (!loading && playerName) {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 8px 25px rgba(255, 107, 53, 0.4)';
              }
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 5px 15px rgba(0,0,0,0.2)';
            }}
          >
            {loading ? "🔄 Buscando..." : "🚀 Buscar"}
          </button>
        </div>

        {error && (
          <div style={{
            textAlign: 'center',
            padding: '15px',
            background: 'linear-gradient(135deg, #FF6B6B, #FF8E8E)',
            color: 'white',
            borderRadius: '10px',
            marginBottom: '20px',
            fontWeight: 'bold',
            boxShadow: '0 5px 15px rgba(255, 107, 107, 0.3)'
          }}>
            ❌ Error: {error}
          </div>
        )}

        {cards.length > 0 && (
          <div style={{
            overflowX: 'auto',
            borderRadius: '15px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
            background: 'white'
          }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontSize: '14px'
            }}>
              <thead>
                <tr style={{
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  color: 'white'
                }}>
                  <th 
                    onClick={() => sortData('Name')}
                    style={{ 
                      padding: '20px 15px', 
                      fontWeight: 'bold', 
                      textAlign: 'center',
                      cursor: 'pointer',
                      userSelect: 'none',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = 'rgba(255, 255, 255, 0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'transparent';
                    }}
                  >
                    🏆 Nombre{getSortIcon('Name')}
                  </th>
                  <th 
                    onClick={() => sortData('card')}
                    style={{ 
                      padding: '20px 15px', 
                      fontWeight: 'bold', 
                      textAlign: 'center',
                      cursor: 'pointer',
                      userSelect: 'none',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = 'rgba(255, 255, 255, 0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'transparent';
                    }}
                  >
                    🎴 Estilo Carta{getSortIcon('card')}
                  </th>
                  <th 
                    onClick={() => sortData('overall_rating')}
                    style={{ 
                      padding: '20px 15px', 
                      fontWeight: 'bold', 
                      textAlign: 'center',
                      cursor: 'pointer',
                      userSelect: 'none',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = 'rgba(255, 255, 255, 0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'transparent';
                    }}
                  >
                    ⭐ Media{getSortIcon('overall_rating')}
                  </th>
                  <th 
                    onClick={() => sortData('price')}
                    style={{ 
                      padding: '20px 15px', 
                      fontWeight: 'bold', 
                      textAlign: 'center',
                      cursor: 'pointer',
                      userSelect: 'none',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = 'rgba(255, 255, 255, 0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'transparent';
                    }}
                  >
                    💰 Precio UT{getSortIcon('price')}
                  </th>
                  <th 
                    onClick={() => sortData('predicted_price')}
                    style={{ 
                      padding: '20px 15px', 
                      fontWeight: 'bold', 
                      textAlign: 'center',
                      cursor: 'pointer',
                      userSelect: 'none',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = 'rgba(255, 255, 255, 0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'transparent';
                    }}
                  >
                    💎 Precio Real{getSortIcon('predicted_price')}
                  </th>
                  <th 
                    onClick={() => sortData('age')}
                    style={{ 
                      padding: '20px 15px', 
                      fontWeight: 'bold', 
                      textAlign: 'center',
                      cursor: 'pointer',
                      userSelect: 'none',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = 'rgba(255, 255, 255, 0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'transparent';
                    }}
                  >
                    🎂 Edad{getSortIcon('age')}
                  </th>
                  <th 
                    onClick={() => sortData('positions')}
                    style={{ 
                      padding: '20px 15px', 
                      fontWeight: 'bold', 
                      textAlign: 'center',
                      cursor: 'pointer',
                      userSelect: 'none',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = 'rgba(255, 255, 255, 0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'transparent';
                    }}
                  >
                    📍 Posición{getSortIcon('positions')}
                  </th>
                  <th 
                    onClick={() => sortData('preferred_foot')}
                    style={{ 
                      padding: '20px 15px', 
                      fontWeight: 'bold', 
                      textAlign: 'center',
                      cursor: 'pointer',
                      userSelect: 'none',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = 'rgba(255, 255, 255, 0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'transparent';
                    }}
                  >
                    🦶 Pie{getSortIcon('preferred_foot')}
                  </th>
                  <th 
                    onClick={() => sortData('height_cm')}
                    style={{ 
                      padding: '20px 15px', 
                      fontWeight: 'bold', 
                      textAlign: 'center',
                      cursor: 'pointer',
                      userSelect: 'none',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = 'rgba(255, 255, 255, 0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'transparent';
                    }}
                  >
                    📏 Altura{getSortIcon('height_cm')}
                  </th>
                  <th 
                    onClick={() => sortData('weight_kg')}
                    style={{ 
                      padding: '20px 15px', 
                      fontWeight: 'bold', 
                      textAlign: 'center',
                      cursor: 'pointer',
                      userSelect: 'none',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = 'rgba(255, 255, 255, 0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'transparent';
                    }}
                  >
                    ⚖️ Peso{getSortIcon('weight_kg')}
                  </th>
                </tr>
              </thead>
              <tbody>
                {sortedCards.map((card, index) => (
                  <tr
                    key={card.player_id + card.card + index}
                    style={{
                      background: index % 2 === 0 
                        ? 'linear-gradient(135deg, #f8f9ff, #e8f0ff)' 
                        : 'linear-gradient(135deg, #fff, #f5f7ff)',
                      transition: 'all 0.3s ease'
                    }}
                  >
                    <td style={{ padding: '25px', textAlign: 'center', fontWeight: 'bold', maxWidth: '150px', overflow: 'hidden' }}>
                      {card.link ? (
                        <a
                          href={card.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            color: '#667eea',
                            textDecoration: 'none',
                            fontWeight: 'bold',
                            padding: '5px 10px',
                            borderRadius: '8px',
                            background: 'linear-gradient(135deg, #e3f2fd, #bbdefb)',
                            transition: 'all 0.3s ease',
                            display: 'inline-block',
                            maxWidth: '150px',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                        }}
                        >
                          {formatValue(card.Name)}
                        </a>
                      ) : (
                        formatValue(card.Name)
                      )}
                    </td>
                    <td style={{ padding: '15px', textAlign: 'center' }}>
                    <span style={{
                        background: getCardTypeColor(card.card),
                        color: 'white',
                        padding: '5px 12px',
                        borderRadius: '20px',
                        fontWeight: 'bold',
                        fontSize: '12px',
                        textShadow: '1px 1px 2px rgba(0,0,0,0.3)',
                        display: 'inline-block',
                        maxWidth: '120px',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                    }}>
                        {formatValue(card.card)}
                    </span>
                    </td>
                    <td style={{ padding: '15px', textAlign: 'center' }}>
                      <span style={{
                        background: getRatingColor(card.overall_rating),
                        color: 'white',
                        padding: '8px 12px',
                        borderRadius: '50%',
                        fontWeight: 'bold',
                        fontSize: '14px',
                        textShadow: '1px 1px 2px rgba(0,0,0,0.3)'
                      }}>
                        {formatValue(card.overall_rating)}
                      </span>
                    </td>
                    <td style={{ padding: '15px', textAlign: 'center', fontWeight: 'bold', color: '#FF6B35' }}>
                      {formatValue(card.price)}
                    </td>
                    <td style={{ padding: '15px', textAlign: 'center', fontWeight: 'bold', color: '#4ECDC4', fontSize: '16px' }}>
                      {formatCurrency(card.predicted_price)}
                    </td>
                    <td style={{ padding: '15px', textAlign: 'center' }}>{formatValue(card.age)}</td>
                    <td style={{ padding: '15px', textAlign: 'center', fontWeight: 'bold', color: '#667eea' }}>
                      {formatValue(card.positions)}
                    </td>
                    <td style={{ padding: '15px', textAlign: 'center' }}>{formatValue(card.preferred_foot)}</td>
                    <td style={{ padding: '15px', textAlign: 'center' }}>{formatValue(card.height_cm)}</td>
                    <td style={{ padding: '15px', textAlign: 'center' }}>{formatValue(card.weight_kg)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {cards.length === 0 && !loading && !error && (
          <div style={{
            textAlign: 'center',
            padding: '40px',
            background: 'linear-gradient(135deg, #f0f8ff, #e6f3ff)',
            borderRadius: '15px',
            marginTop: '20px',
            color: '#667eea',
            fontSize: '18px',
            fontWeight: 'bold'
          }}>
            🎮 Ingrese un nombre de jugador y presione Buscar para comenzar
          </div>
        )}
      </div>
    </div>
  );
}