import './App.css';
import { FormEvent, useState } from 'react';
import axios from 'axios';
import { 
  ChakraProvider, Select, Input, Button, HStack, Box, Spinner, SimpleGrid, Center, Text
} from '@chakra-ui/react'
import { Product } from './components/Product';

function App() {
  const [apiValue, setApiValue] = useState([]);
  const [searchOptions, setSearchOptions] = useState({
    store: '',
    searchTerm: '',
    zipCode: '',
    city: '',
  });
  const [isSearching, setIsSearching] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [searchRun, setSearchRun] = useState(false);

  const handleSearch = async () => {
    setSearchRun(true);
    const { store, searchTerm, zipCode, city } = searchOptions;
    setErrorMessage('');
    setApiValue([]);
    setIsSearching(true);
    try {
      const requestUrl = encodeURI(`api/prices/${store}?search_term=${searchTerm}&zip_code=${zipCode}&city_name=${city}`)
      const response = await axios.get(requestUrl);
      if (response.status === 200) {
        setApiValue(response.data);
      }
      setIsSearching(false);
    } catch (err) {
      console.error(err);
      setErrorMessage('There was a problem with getting the results.')
      setIsSearching(false);
    }
  }

  type SearchOptionTypes = 'store' | 'searchTerm' | 'zipCode' | 'city'

  const handleOptionChange = (e: FormEvent, optionName: SearchOptionTypes) => {
    const target = e.target as HTMLInputElement;
    const newOptions = { ...searchOptions };
    newOptions[optionName] = target.value;
    setSearchOptions({ ...newOptions });
  };

  const disableSearch = () => (
    isSearching || searchOptions.store.length === 0 || 
    searchOptions.city.length === 0 || 
    searchOptions.zipCode.length === 0 ||
    searchOptions.searchTerm.length === 0
  );

  return (
    <ChakraProvider>
      <Box mt={5}>
        <HStack justify='center'>
          <Select 
            w='150px'
            placeholder='Select a store' 
            onChange={(e) => handleOptionChange(e, 'store')}
          >
            <option value={0}>Aldi</option>
            <option value={1}>Wegmans</option>
          </Select>
          <Input 
            w='200px'
            variant='outline'
            placeholder='Enter search term'
            onChange={(e) => handleOptionChange(e, 'searchTerm')}
          />
          <Input 
            w='200px'
            variant='outline' 
            placeholder='Enter zip code' 
            onChange={(e) => handleOptionChange(e, 'zipCode')}
          />
          <Input 
            w='200px'
            variant='outline'
            placeholder='Enter city name' 
            onChange={(e) => handleOptionChange(e, 'city')}
          />
          <Box w='50px'>
            <Button onClick={handleSearch} isDisabled={disableSearch()}>Search</Button>
          </Box>
        </HStack>
          { errorMessage !== '' ? <Center height='80vh'><Text size='xl'>{errorMessage}</Text></Center> : null }
        { 
          isSearching ? 
          <HStack height='80vh' justify='center' align='center'>
            <p>Loading results</p>
            <Spinner />
          </HStack>
          :
          <Center>
            {
              apiValue.length > 0 ?
              <SimpleGrid minChildWidth='200px' spacing='30px' width='70vw' height='80vh' mt={5}>
                {
                  apiValue.map((item) => (
                    <Product 
                      key={`${item['name']},${item['price']}`}
                      name={item['name']}
                      price={item['price']}
                      quantity={item['quantity']}
                      isInStock={item['is_in_stock']}
                      imageUrl={item['image_url']}
                    />
                  ))
                }
              </SimpleGrid>
              :
              (
                searchRun && searchOptions.searchTerm.length > 0 && errorMessage === '' ?
                <Center height='80vh'>
                  <Text fontSize='xl'>
                    {`There were no results for ${searchOptions.searchTerm}`}
                  </Text>
                </Center>
                :
                null
              )
            }
          </Center>
        }
      </Box>
    </ChakraProvider>
  );
}

export default App;
