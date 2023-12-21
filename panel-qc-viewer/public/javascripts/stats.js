export function stdDev(arr) { 

    // Creating the mean with Array.reduce
    let mean = arr.reduce((acc, curr) => {
        return acc + curr
    }, 0) / arr.length;
 
    // Assigning (value - mean) ^ 2 to
    // every array item
    arr = arr.map((k) => {
        return (k - mean) ** 2
    });
 
    // Calculating the sum of updated array 
    let sum = arr.reduce((acc, curr) => acc + curr, 0);
 
    // Calculating the variance
    let variance = sum / arr.length
 
    // Returning the standard deviation
    return Math.sqrt(sum / arr.length)
}
