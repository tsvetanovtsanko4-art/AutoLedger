// Fill-to-fill method: the litres put in at a stop were burnt since the previous stop.
// Same calculation as GET /api/cars/{id}/avg-consumption.
export function consumptionPerStop(refuelings) {
    const sorted = [...refuelings].sort((a, b) => a.odometer - b.odometer);
    return sorted.map((refuel, i) => {
        const prev = sorted[i - 1];
        const km = prev ? refuel.odometer - prev.odometer : 0;
        const litresPer100km = refuel.quantity_liters && km > 0 ? (refuel.quantity_liters / km) * 100 : null;
        return { ...refuel, litresPer100km };
    });
}

export function averageConsumption(refuelings) {
    const values = consumptionPerStop(refuelings)
        .map(r => r.litresPer100km)
        .filter(v => v !== null);
    if (values.length === 0) return null;
    return Math.round((values.reduce((sum, v) => sum + v, 0) / values.length) * 100) / 100;
}
