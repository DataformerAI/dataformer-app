export async function readJsonFile(path: string): Promise<any> {
  try {
    const response = await fetch(path);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const fileContent = await response.json();
    return fileContent;
  } catch (error) {
    console.error("Error fetching JSON file:", error);
    throw error; // Optionally handle or propagate the error further
  }
}
